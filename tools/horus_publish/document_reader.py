#!/usr/bin/env python3
"""Separate read-only OAuth capability; publisher credentials are never replaced."""
import contextlib
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import types
import urllib.parse
import urllib.request

from publisher import (ACCOUNT, STATE, Drive, NoRedirect, PublishError,
                       FOLDER_MIME, read_private, write_private, state_dir,
                       private_path, require_account)
from drive_sync import checked_id, selected_store

READER_SCOPE = "https://www.googleapis.com/auth/drive.readonly"


def validate_token(token, client):
    if (set(token.get("scopes", [])) != {READER_SCOPE}
            or token.get("token_uri") != "https://oauth2.googleapis.com/token"
            or any(token.get(k) != client.get(k) for k in ("client_id", "client_secret"))
            or not all(isinstance(token.get(k), str) and token[k]
                       for k in ("token", "refresh_token", "expiry"))):
        raise PublishError("READER_TOKEN_CLIENT_OR_SCOPE_MISMATCH")


def load_selection(base=STATE):
    value = json.loads(read_private(Path(base) / "reader/selection.json"))
    if (set(value) != {"schema", "roots"} or type(value["schema"]) is not int
            or value["schema"] != 1 or not isinstance(value["roots"], list)
            or len(value["roots"]) != 1):
        raise PublishError("READER_SELECTION_INVALID")
    checked_id(value["roots"][0])
    return value


@contextlib.contextmanager
def reader_lock(path):
    state_dir(path)
    fd = os.open(path / "auth.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a") as lock:
        private_path(path / "auth.lock")
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


class ReaderDrive(Drive):
    def __init__(self, base=STATE):
        self.base = Path(base)
        self.path = self.base / "reader"
        self.allowed_roots = load_selection(self.base)["roots"]
        self.opener = urllib.request.build_opener(NoRedirect())
        client = json.loads(read_private(self.base / "client.json"))["installed"]
        with reader_lock(self.path):
            token = json.loads(read_private(self.path / "token.json"))
            validate_token(token, client)
            try:
                expiry = dt.datetime.fromisoformat(token["expiry"].replace("Z", "+00:00"))
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=dt.timezone.utc)
            except ValueError:
                expiry = dt.datetime.min.replace(tzinfo=dt.timezone.utc)
            if expiry <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=90):
                token = self.refresh(token)
                write_private(self.path / "token.json", json.dumps(token).encode())
        self.creds = types.SimpleNamespace(token=token["token"])

    def refresh(self, token):
        # A separate grant and endpoint, never publisher.Drive.refresh's drive.file.
        try:
            params = {k: token[k] for k in ("client_id", "client_secret", "refresh_token")}
            params["grant_type"] = "refresh_token"
            request = urllib.request.Request("https://oauth2.googleapis.com/token",
                data=urllib.parse.urlencode(params).encode(),
                headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
            with self.opener.open(request, timeout=25) as response:
                raw = response.read(20001)
            if len(raw) > 20000:
                raise ValueError
            value = json.loads(raw)
            if (value.get("token_type") != "Bearer" or not isinstance(value.get("access_token"), str) or not value["access_token"]
                    or type(value.get("expires_in")) is not int
                    or not 1 <= value["expires_in"] <= 86400):
                raise ValueError
        except Exception:
            raise PublishError("READER_REFRESH_FAILED_AUTHORIZE_PRIVATELY") from None
        if "scope" in value and set(value["scope"].split()) != {READER_SCOPE}:
            raise PublishError("READER_SCOPE_MISMATCH")
        result = dict(token, token=value["access_token"],
            expiry=(dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=value["expires_in"])).isoformat())
        if value.get("refresh_token"):
            result["refresh_token"] = value["refresh_token"]
        return result

    def call(self, path, *, method="GET", obj=None, data=None, content_type=None, media=False, upload=False):
        parsed = urllib.parse.urlsplit(path)
        allowed = (parsed.path in {"about", "files", "changes", "changes/startPageToken"}
                   or re.fullmatch(r"files/[A-Za-z0-9_-]{10,100}(/export)?", parsed.path))
        if (method != "GET" or obj is not None or data is not None or upload
                or parsed.scheme or parsed.netloc or parsed.fragment or not allowed
                or parsed.path == "files/generateIds"):
            raise PublishError("READER_READ_ONLY_OPERATION_REQUIRED")
        return super().call(path, media=media)


def open_reader(base=STATE):
    marker = Path(base) / "reader/selection.json"
    if marker.exists() or marker.is_symlink():
        return ReaderDrive(base)
    return Drive(base)


def reader_state(drive, state):
    from drive_browser import metadata, public_file
    folders = []
    for root in drive.allowed_roots:
        try:
            item = dict(public_file(metadata(drive, root, folder=True)),
                        enabled=root in state["enabled"], available=True)
        except PublishError:
            item = dict(id=root, name="MESTRY no disponible", folder=True,
                        mime_type=FOLDER_MIME, enabled=root in state["enabled"], available=False)
        folders.append(item)
    by_id = {item["id"]: item for item in folders}
    return {"status": "OK", "scope": "drive.readonly", "folders": folders,
            "assignments": [{"project": project, "folder": by_id[root]}
                            for project, root in state["assignments"].items() if root in by_id],
            "unavailable_enabled": [item["id"] for item in folders if item["enabled"] and not item["available"]],
            "more_folders_available": False}


def prepare_authorization(base=STATE):
    """Only the private user-run helper consumes this response; contains client data."""
    from drive_browser import load_state
    from oauth_setup import validate_client
    base = Path(base)
    if (base / "reader/selection.json").exists():
        raise PublishError("READER_ALREADY_CONFIGURED_NO_AUTOMATIC_RECONSENT")
    roots = load_state(base)["enabled"]
    if len(roots) != 1:
        raise PublishError("READER_SINGLE_SELECTED_ROOT_REQUIRED")
    return {"client": validate_client(read_private(base / "client.json")),
            "roots": roots, "account": ACCOUNT}


def commit_authorization(payload, base=STATE):
    """Validate natively before activating; retain publisher token byte-for-byte."""
    from drive_browser import load_state
    from oauth_setup import validate_client
    from drive_sync import DriveAPI
    base = Path(base)
    roots = payload.get("roots")
    if not isinstance(roots, list) or len(roots) != 1:
        raise PublishError("READER_SINGLE_SELECTED_ROOT_REQUIRED")
    checked_id(roots[0])
    # Same lock order as the controlled broker update.
    with contextlib.ExitStack() as stack:
        for name in ("drive-browser.lock", "publisher.lock"):
            fd = os.open(base / name, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            handle = stack.enter_context(os.fdopen(fd, "a"))
            private_path(base / name)
            fcntl.flock(handle, fcntl.LOCK_EX)
        if (base / "reader/selection.json").exists():
            raise PublishError("READER_ALREADY_CONFIGURED")
        if load_state(base)["enabled"] != roots:
            raise PublishError("READER_SELECTION_CHANGED")
        client = validate_client(read_private(base / "client.json"))["installed"]
        token = payload.get("token", {})
        validate_token(token, client)
        # Keep every publisher-owned byte; this refresh is validation in memory.
        writer_before = read_private(base / "token.json")
        writer = Drive.__new__(Drive)
        writer.path = base
        writer.opener = urllib.request.build_opener(NoRedirect())
        writer_token = writer.refresh(json.loads(writer_before))
        writer.creds = types.SimpleNamespace(token=writer_token["token"])
        require_account(writer)
        reader = ReaderDrive.__new__(ReaderDrive)
        reader.base, reader.path = base, base / "reader"
        reader.allowed_roots = roots
        reader.opener = urllib.request.build_opener(NoRedirect())
        token = reader.refresh(token)
        reader.creds = types.SimpleNamespace(token=token["token"])
        require_account(reader)
        root = DriveAPI(reader).metadata(roots[0])
        if root.get("trashed") or root.get("mimeType") != FOLDER_MIME:
            raise PublishError("READER_ROOT_UNAVAILABLE")
        state_dir(base / "reader")
        with selected_store(base, ACCOUNT, roots[0]) as store:
            with store.db:
                store.set("rescan", 1)  # New permission sees older files absent from drive.file.
        # Activation marker last; cancellation/failure keeps the old reader active.
        write_private(base / "reader/token.json", json.dumps(token).encode())
        write_private(base / "reader/selection.json", json.dumps({"schema": 1, "roots": roots}).encode())
        if read_private(base / "token.json") != writer_before:
            raise PublishError("READER_PUBLISHER_TOKEN_CHANGED")
    return {"status": "READER_AUTHORIZED", "scope": "drive.readonly",
            "selected_roots": 1, "native_refresh_verified": True,
            "publisher_refresh_verified": True, "publisher_token_preserved": True,
            "remote_files_modified": False}

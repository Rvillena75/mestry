#!/usr/bin/env python3
"""Drive browsing capability for the paired app; OAuth stays in Termux.

Google's per-file grant and the app's enabled-folder list are independent.
This module never creates, edits, moves, deletes, or shares a Drive resource.
"""
import contextlib
import fcntl
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import urllib.parse

from publisher import (Drive, DriveError, FOLDER_MIME, PublishError, STATE,
                       no_duplicates, private_path, read_config, read_private,
                       require_account, state_dir, write_private)

PROJECT = "/workspace/projects/mestry-horus-smoke"
META = "id,name,mimeType,parents,trashed,modifiedTime,size"
ID = re.compile(r"[A-Za-z0-9_-]{10,100}\Z")
OPS = {"state", "folder.enable", "assign", "list", "read"}


def file_id(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise PublishError("DRIVE_FILE_ID_INVALID")
    return value


def parse_request(raw):
    if len(raw) > 10000:
        raise PublishError("DRIVE_REQUEST_TOO_LARGE")
    try:
        obj = json.loads(raw, object_pairs_hook=no_duplicates)
    except (ValueError, UnicodeError):
        raise PublishError("DRIVE_REQUEST_INVALID") from None
    if not isinstance(obj, dict) or obj.get("op") not in OPS or obj.get("schema") != 1 or type(obj.get("schema")) is not int:
        raise PublishError("DRIVE_REQUEST_INVALID")
    fields = {"state": set(), "folder.enable": {"folder_id", "enabled"},
              "assign": {"project", "folder_id"},
              "list": {"root_id", "folder_id", "page_token"},
              "read": {"root_id", "file_id"}}[obj["op"]]
    if set(obj) != fields | {"op", "schema"}:
        raise PublishError("DRIVE_REQUEST_FIELDS")
    for key in ("root_id", "folder_id", "file_id"):
        if key in obj and not (key == "folder_id" and obj["op"] == "assign" and obj[key] is None):
            file_id(obj[key])
    if "project" in obj and obj["project"] != PROJECT:
        raise PublishError("DRIVE_PROJECT_NOT_ALLOWED")
    if "enabled" in obj and type(obj["enabled"]) is not bool:
        raise PublishError("DRIVE_ENABLED_BOOLEAN_REQUIRED")
    if "page_token" in obj and (not isinstance(obj["page_token"], str) or len(obj["page_token"]) > 4096):
        raise PublishError("DRIVE_PAGE_TOKEN_INVALID")
    return obj


def metadata(drive, value, folder=False):
    value = file_id(value)
    try:
        result = drive.call("files/" + value + "?" + urllib.parse.urlencode({"fields": META}))
    except DriveError as error:
        if error.status in (403, 404):
            raise PublishError("DRIVE_FILE_NOT_GRANTED_OR_UNAVAILABLE") from None
        raise
    if result.get("id") != value or result.get("trashed") is not False:
        raise PublishError("DRIVE_FILE_UNAVAILABLE")
    if folder and result.get("mimeType") != FOLDER_MIME:
        raise PublishError("DRIVE_FOLDER_REQUIRED")
    return result


def public_file(meta):
    value = file_id(meta.get("id"))
    return {"id": value, "name": str(meta.get("name", ""))[:1000],
            "mime_type": meta.get("mimeType", ""),
            "folder": meta.get("mimeType") == FOLDER_MIME,
            "modified_time": meta.get("modifiedTime"), "size": meta.get("size"),
            "url": ("https://drive.google.com/drive/folders/" if meta.get("mimeType") == FOLDER_MIME
                    else "https://drive.google.com/file/d/") + value + ("" if meta.get("mimeType") == FOLDER_MIME else "/view")}


def default_state(path):
    # Discover only the already installed publisher folder; do not alter its journal.
    db_path = path / "journal.sqlite3"
    private_path(db_path)
    with contextlib.closing(sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True)) as conn:
        row = conn.execute("SELECT file_id FROM folder WHERE singleton=1").fetchone()
    if not row:
        return {"schema": 1, "enabled": [], "assignments": {}}
    root = file_id(row[0])
    return {"schema": 1, "enabled": [root], "assignments": {PROJECT: root}}


def load_state(path):
    target = path / "drive-browser.json"
    state = json.loads(read_private(target)) if target.exists() or target.is_symlink() else default_state(path)
    if (set(state) != {"schema", "enabled", "assignments"} or state["schema"] != 1
            or not isinstance(state["enabled"], list) or len(state["enabled"]) > 32
            or len(set(state["enabled"])) != len(state["enabled"])
            or not isinstance(state["assignments"], dict)
            or any(k != PROJECT or v not in state["enabled"] for k, v in state["assignments"].items())):
        raise PublishError("DRIVE_BROWSER_STATE_INVALID")
    for value in state["enabled"]:
        file_id(value)
    return state


def list_page(drive, query, token=""):
    params = {"q": query + " and trashed=false", "spaces": "drive", "pageSize": 100,
              "fields": "nextPageToken,incompleteSearch,files(" + META + ")",
              "orderBy": "folder,name_natural", "pageToken": token}
    value = drive.call("files?" + urllib.parse.urlencode(params))
    if not isinstance(value.get("files"), list) or len(value["files"]) > 100:
        raise PublishError("DRIVE_LIST_RESPONSE_INVALID")
    return value


def state_response(drive, state):
    folders, seen, token = [], set(), ""
    for _ in range(5):
        page = list_page(drive, "mimeType='" + FOLDER_MIME + "'", token)
        for meta in page["files"]:
            if meta.get("trashed") is not False or meta.get("mimeType") != FOLDER_MIME:
                continue
            item = public_file(meta)
            if item["id"] not in seen:
                folders.append(dict(item, enabled=item["id"] in state["enabled"]))
                seen.add(item["id"])
        token = page.get("nextPageToken", "")
        if not token:
            break
    # An explicitly enabled folder may fall beyond the first 500 results.
    unavailable = []
    for value in state["enabled"]:
        if value in seen:
            continue
        try:
            folders.append(dict(public_file(metadata(drive, value, folder=True)), enabled=True, available=True))
            seen.add(value)
        except PublishError:
            unavailable.append(value)
            # Keep the local choice visible so the user can disable it even if
            # Google access was revoked or an ancestor was put in the trash.
            folders.append({"id": value, "name": "Carpeta no disponible",
                            "folder": True, "mime_type": FOLDER_MIME,
                            "enabled": True, "available": False})
    names = {item["id"]: item for item in folders}
    return {"status": "OK", "scope": "drive.file", "folders": folders,
            "assignments": [{"project": key, "folder": names[value]} for key, value in state["assignments"].items() if value in names],
            "unavailable_enabled": unavailable, "more_folders_available": bool(token)}


def within_root(drive, value, root, enabled, *, folder=False):
    if root not in enabled:
        raise PublishError("DRIVE_FOLDER_DISABLED")
    metadata(drive, root, folder=True)  # A revoked root never permits cached access.
    original = metadata(drive, value, folder=folder)
    current, seen = original, set()
    for _ in range(33):
        here = file_id(current.get("id"))
        if here == root:
            return original
        if here in seen:
            break
        seen.add(here)
        parents = current.get("parents", [])
        if len(parents) != 1:
            break
        current = metadata(drive, parents[0], folder=True)
    raise PublishError("DRIVE_ITEM_OUTSIDE_ENABLED_FOLDER")


def handle(drive, state, obj, save):
    op = obj["op"]
    if op == "state":
        return state_response(drive, state)
    if op == "folder.enable":
        value = obj["folder_id"]
        if obj["enabled"]:
            metadata(drive, value, folder=True)
            if value not in state["enabled"]:
                if len(state["enabled"]) >= 32:
                    raise PublishError("DRIVE_ENABLED_FOLDER_LIMIT")
                state["enabled"].append(value)
        else:
            state["enabled"] = [v for v in state["enabled"] if v != value]
            state["assignments"] = {k: v for k, v in state["assignments"].items() if v != value}
        save(state)
        return state_response(drive, state)
    if op == "assign":
        value = obj["folder_id"]
        if value is None:
            state["assignments"].pop(obj["project"], None)
        else:
            if value not in state["enabled"]:
                raise PublishError("DRIVE_FOLDER_DISABLED")
            metadata(drive, value, folder=True)
            state["assignments"][obj["project"]] = value
        save(state)
        return state_response(drive, state)
    root = obj["root_id"]
    value = obj["folder_id"] if op == "list" else obj["file_id"]
    meta = within_root(drive, value, root, state["enabled"], folder=op == "list")
    if op == "list":
        page = list_page(drive, "'" + value + "' in parents", obj["page_token"])
        # Never follow shortcuts. Only direct children returned by Google are shown.
        files = [public_file(m) for m in page["files"] if m.get("parents") == [value] and m.get("trashed") is False]
        return {"status": "OK", "folder": public_file(meta), "files": files,
                "next_page_token": page.get("nextPageToken", ""),
                "incomplete": page.get("incompleteSearch", False)}
    item = public_file(meta)
    mime = meta.get("mimeType", "")
    if mime == "application/vnd.google-apps.document":
        route = "files/" + value + "/export?mimeType=text%2Fplain"
    elif mime.startswith("text/") or mime in {"application/json", "application/xml"}:
        route = "files/" + value + "?alt=media"
    else:
        return {"status": "OPEN_IN_DRIVE", "file": item}
    try:
        content = drive.call(route, media=True).decode("utf-8")
    except (UnicodeError, PublishError) as error:
        if isinstance(error, PublishError) and str(error) != "DRIVE_RESPONSE_TOO_LARGE":
            raise
        return {"status": "OPEN_IN_DRIVE", "file": item}
    return {"status": "OK", "file": item, "text": content}


def main():
    obj = parse_request(sys.stdin.buffer.read(10001))
    read_config()
    state_dir()
    lock_path = STATE / "drive-browser.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a") as lock:
        private_path(lock_path)
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = load_state(STATE)
        drive = Drive()
        require_account(drive)
        return handle(drive, state, obj, lambda value: write_private(STATE / "drive-browser.json", json.dumps(value).encode()))

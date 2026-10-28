#!/usr/bin/env python3
"""Bounded append-only Drive publisher; invoked through a restricted SSH key."""
import base64
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import sys
import tempfile
import types
import urllib.error
import urllib.parse
import urllib.request
import uuid

SCOPE = "https://www.googleapis.com/auth/drive.file"
ACCOUNT = "owner@example.invalid"
REVIEW_ID = "DRIVE_FOLDER_03_EXAMPLE"
DOCUMENT = "S23_PUBLISH_TEST.md"
PUBLISHER = "mestry-s23-v1"
MAX_BYTES = 65536
MAX_REQUEST = 90000
STATE = Path.home() / ".local/state/mestry-publish"
CODE = Path(__file__).resolve().parent
FOLDER_MIME = "application/vnd.google-apps.folder"
FIELDS = ("id,name,mimeType,parents,trashed,ownedByMe,"
          "owners(emailAddress),permissions(type,role,emailAddress),appProperties")


class PublishError(Exception):
    """Only fixed, non-sensitive codes are returned to the caller."""


class DriveError(PublishError):
    def __init__(self, status):
        self.status = status
        super().__init__(f"DRIVE_HTTP_{status}")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def request_id(digest):
    return sha((DOCUMENT + "\0" + digest).encode("ascii"))


def no_duplicates(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise PublishError("DUPLICATE_JSON_KEY")
        result[k] = v
    return result


def parse_request(raw):
    if len(raw) > MAX_REQUEST:
        raise PublishError("REQUEST_TOO_LARGE")
    try:
        obj = json.loads(raw, object_pairs_hook=no_duplicates)
        if not isinstance(obj, dict) or set(obj) != {
            "schema", "document", "sha256", "request_id", "content_base64"
        }:
            raise PublishError("REQUEST_FIELDS")
        if type(obj["schema"]) is not int or obj["schema"] != 1:
            raise PublishError("REQUEST_SCHEMA")
        if obj["document"] != DOCUMENT:
            raise PublishError("DOCUMENT_NOT_ALLOWED")
        if not isinstance(obj["sha256"], str) or not re.fullmatch("[a-f0-9]{64}", obj["sha256"]):
            raise PublishError("CONTENT_HASH_INVALID")
        data = base64.b64decode(obj["content_base64"], validate=True)
        if not data or len(data) > MAX_BYTES:
            raise PublishError("CONTENT_SIZE")
        text = data.decode("utf-8")
        if any(ord(c) < 32 and c not in "\r\n\t" for c in text) or "\x7f" in text:
            raise PublishError("CONTENT_CONTROL_CHARACTER")
        if sha(data) != obj["sha256"] or obj["request_id"] != request_id(sha(data)):
            raise PublishError("CONTENT_HASH_MISMATCH")
        return obj, data
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise PublishError("REQUEST_INVALID") from None


def private_path(path, directory=False):
    info = path.lstat()
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if (not expected(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        raise PublishError("PRIVATE_PATH_UNSAFE")


def state_dir(path=STATE):
    # Android's private home is the trust root; reject redirected descendants.
    home = Path.home()
    if path == STATE:
        for p in (home / ".local", home / ".local/state"):
            if p.is_symlink():
                raise PublishError("PRIVATE_PATH_UNSAFE")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    private_path(path, directory=True)
    return path


def read_private(path, limit=100000):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as f:
        info = os.fstat(f.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise PublishError("PRIVATE_PATH_UNSAFE")
        raw = f.read(limit + 1)
    if len(raw) > limit:
        raise PublishError("PRIVATE_FILE_TOO_LARGE")
    return raw


def write_private(path, raw):
    state_dir(path.parent)
    if path.exists() or path.is_symlink():
        private_path(path)
    fd, name = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            os.fchmod(f.fileno(), 0o600)
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
        dfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_config(path=STATE):
    config = json.loads(read_private(path / "config.json"))
    if config.get("account") != ACCOUNT or config.get("review_id") != REVIEW_ID:
        raise PublishError("CONFIG_TARGET_MISMATCH")
    return config


@contextlib.contextmanager
def journal(path=STATE):
    state_dir(path)
    fd = os.open(path / "publisher.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a") as lock:
        private_path(path / "publisher.lock")
        fcntl.flock(lock, fcntl.LOCK_EX)
        db_path = path / "journal.sqlite3"
        if db_path.exists() or db_path.is_symlink():
            private_path(db_path)
        conn = sqlite3.connect(db_path)
        try:
            os.chmod(db_path, 0o600)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("CREATE TABLE IF NOT EXISTS folder (singleton INTEGER PRIMARY KEY CHECK(singleton=1), file_id TEXT NOT NULL)")
            conn.execute("""CREATE TABLE IF NOT EXISTS publication (
                seq INTEGER PRIMARY KEY, request_id TEXT UNIQUE NOT NULL,
                digest TEXT NOT NULL, file_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL, created_day TEXT NOT NULL, verified INTEGER NOT NULL DEFAULT 0)""")
            conn.commit()
            yield conn
        finally:
            conn.close()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Drive:
    def __init__(self, path=STATE):
        self.path = path
        obj = json.loads(read_private(path / "token.json"))
        if set(obj.get("scopes", [])) != {SCOPE} or obj.get("token_uri") != "https://oauth2.googleapis.com/token":
            raise PublishError("OAUTH_SCOPE_MISMATCH")
        self.opener = urllib.request.build_opener(NoRedirect())
        try:
            expiry = dt.datetime.fromisoformat(obj.get("expiry", "").replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=dt.timezone.utc)
        except ValueError:
            expiry = dt.datetime.min.replace(tzinfo=dt.timezone.utc)
        if not obj.get("token") or expiry <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=90):
            obj = self.refresh(obj)
            write_private(path / "token.json", json.dumps(obj).encode())
        self.creds = types.SimpleNamespace(token=obj["token"])

    def refresh(self, obj):
        # Standard refresh grant; no interactive authorization or JWT signing on S23.
        try:
            params = {k: obj[k] for k in ("client_id", "client_secret", "refresh_token")}
            params["grant_type"] = "refresh_token"
            req = urllib.request.Request("https://oauth2.googleapis.com/token",
                data=urllib.parse.urlencode(params).encode(),
                headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
            with self.opener.open(req, timeout=25) as response:
                raw = response.read(20001)
            if len(raw) > 20000:
                raise ValueError
            value = json.loads(raw)
            if value.get("token_type") != "Bearer" or not isinstance(value.get("access_token"), str) or not value["access_token"]:
                raise ValueError
            expires = value["expires_in"]
            if type(expires) is not int or not 1 <= expires <= 86400:
                raise ValueError
        except Exception:
            raise PublishError("OAUTH_REFRESH_FAILED_REAUTHORIZE_PRIVATELY") from None
        if "scope" in value and set(value["scope"].split()) != {SCOPE}:
            raise PublishError("OAUTH_SCOPE_MISMATCH")
        updated = dict(obj, token=value["access_token"],
                       expiry=(dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=expires)).isoformat())
        if "refresh_token" in value:
            updated["refresh_token"] = value["refresh_token"]
        return updated

    def call(self, path, *, method="GET", obj=None, data=None, content_type=None, media=False, upload=False):
        base = "https://www.googleapis.com/" + ("upload/drive/v3/" if upload else "drive/v3/")
        headers = {"Authorization": "Bearer " + self.creds.token}
        if obj is not None:
            data = json.dumps(obj).encode()
            content_type = "application/json; charset=UTF-8"
        if content_type:
            headers["Content-Type"] = content_type
        req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=25) as r:
                raw = r.read((MAX_BYTES if media else 100000) + 1)
        except urllib.error.HTTPError as e:
            raise DriveError(e.code) from None
        except (OSError, TimeoutError):
            raise PublishError("DRIVE_RESPONSE_UNKNOWN_RETRY_SAME_CONTENT") from None
        if len(raw) > (MAX_BYTES if media else 100000):
            raise PublishError("DRIVE_RESPONSE_TOO_LARGE")
        try:
            return raw if media else json.loads(raw)
        except (ValueError, UnicodeError):
            raise PublishError("DRIVE_RESPONSE_INVALID_RETRY_SAME_CONTENT") from None

    def account(self):
        return self.call("about?fields=user(emailAddress)")["user"]["emailAddress"]

    def generate_id(self):
        value = self.call("files/generateIds?count=1&space=drive&type=files")["ids"][0]
        if not re.fullmatch(r"[A-Za-z0-9_-]{10,100}", value):
            raise PublishError("DRIVE_ID_INVALID")
        return value

    def metadata(self, file_id):
        return self.call("files/" + urllib.parse.quote(file_id, safe="") + "?" + urllib.parse.urlencode({"fields": FIELDS}))

    def download(self, file_id):
        return self.call("files/" + urllib.parse.quote(file_id, safe="") + "?alt=media", media=True)

    def create(self, metadata, content=None):
        if content is None:
            return self.call("files?fields=id", method="POST", obj=metadata)
        boundary = "mestry_" + uuid.uuid4().hex
        body = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode()
                + json.dumps(metadata).encode()
                + f"\r\n--{boundary}\r\nContent-Type: text/markdown; charset=UTF-8\r\n\r\n".encode()
                + content + f"\r\n--{boundary}--\r\n".encode())
        return self.call("files?uploadType=multipart&fields=id", method="POST", data=body,
                         content_type="multipart/related; boundary=" + boundary, upload=True)


def require_account(drive):
    if drive.account().lower() != ACCOUNT:
        raise PublishError("DRIVE_ACCOUNT_MISMATCH")


def require_private(meta):
    if meta.get("trashed") or meta.get("ownedByMe") is not True:
        raise PublishError("DRIVE_OWNER_OR_TRASH_MISMATCH")
    if {p.get("emailAddress", "").lower() for p in meta.get("owners", [])} != {ACCOUNT}:
        raise PublishError("DRIVE_OWNER_MISMATCH")
    permissions = meta.get("permissions", [])
    if len(permissions) != 1 or any(
        p.get("type") != "user" or p.get("role") != "owner"
        or p.get("emailAddress", "").lower() != ACCOUNT for p in permissions
    ):
        raise PublishError("DRIVE_NOT_PRIVATE")


def require_folder(meta, file_id, *, ready=True):
    require_private(meta)
    if (meta.get("id") != file_id or meta.get("mimeType") != FOLDER_MIME
            or meta.get("appProperties") != {"publisher": PUBLISHER, "kind": "review-folder"}):
        raise PublishError("DRIVE_FOLDER_MISMATCH")
    if ready and meta.get("parents") != [REVIEW_ID]:
        raise PublishError("DRIVE_FOLDER_MOVE_TO_REVIEW_REQUIRED")


def get_or_create(drive, metadata, content=None):
    # Never allocate a replacement ID on timeout/409. The reservation is durable.
    try:
        return drive.metadata(metadata["id"])
    except DriveError as e:
        if e.status != 404:
            raise
    try:
        drive.create(metadata, content)
    except DriveError as e:
        if e.status != 409:
            raise
    return drive.metadata(metadata["id"])


def prepare_folder(drive, conn):
    require_account(drive)
    row = conn.execute("SELECT file_id FROM folder WHERE singleton=1").fetchone()
    if row is None:
        file_id = drive.generate_id()
        conn.execute("INSERT INTO folder VALUES (1, ?)", (file_id,))
        conn.commit()
    else:
        file_id = row["file_id"]
    meta = get_or_create(drive, {"id": file_id, "name": "Horus", "mimeType": FOLDER_MIME,
        "appProperties": {"publisher": PUBLISHER, "kind": "review-folder"}})
    require_folder(meta, file_id, ready=False)
    return {"status": "FOLDER_READY" if meta.get("parents") == [REVIEW_ID] else "MOVE_FOLDER_TO_REVIEW_REQUIRED",
            "folder_id": file_id, "url": "https://drive.google.com/drive/folders/" + file_id}


def publish(drive, conn, obj, content, *, day=None):
    require_account(drive)
    folder = conn.execute("SELECT file_id FROM folder WHERE singleton=1").fetchone()
    if folder is None:
        raise PublishError("FOLDER_NOT_PREPARED")
    folder_id = folder["file_id"]
    require_folder(drive.metadata(folder_id), folder_id)
    row = conn.execute("SELECT * FROM publication WHERE request_id=?", (obj["request_id"],)).fetchone()
    if row is None:
        day = day or dt.datetime.now(dt.timezone.utc).date().isoformat()
        total = conn.execute("SELECT COUNT(*) FROM publication").fetchone()[0]
        daily = conn.execute("SELECT COUNT(*) FROM publication WHERE created_day=?", (day,)).fetchone()[0]
        if total >= 32 or daily >= 20:
            raise PublishError("PILOT_QUOTA_REACHED")
        file_id = drive.generate_id()
        seq = total + 1
        name = f"S23_PUBLISH_TEST.r{seq:04d}.{obj['sha256'][:8]}.md"
        conn.execute("INSERT INTO publication (seq,request_id,digest,file_id,name,created_day) VALUES (?,?,?,?,?,?)",
                     (seq, obj["request_id"], obj["sha256"], file_id, name, day))
        conn.commit()
        row = conn.execute("SELECT * FROM publication WHERE request_id=?", (obj["request_id"],)).fetchone()
    if row["digest"] != sha(content):
        raise PublishError("JOURNAL_CONTENT_MISMATCH")
    metadata = {"id": row["file_id"], "name": row["name"], "mimeType": "text/markdown",
                "parents": [folder_id], "appProperties": {
                    "publisher": PUBLISHER, "request_id": obj["request_id"], "sha256": obj["sha256"]}}
    if row["verified"]:
        # A human may have changed it since the previous verification. Never recreate it.
        meta = drive.metadata(row["file_id"])
    else:
        meta = get_or_create(drive, metadata, content)
    require_private(meta)
    if any(meta.get(k) != v for k, v in metadata.items()):
        raise PublishError("REMOTE_METADATA_CHANGED_NO_OVERWRITE")
    if sha(drive.download(row["file_id"])) != obj["sha256"]:
        raise PublishError("REMOTE_CONTENT_CHANGED_NO_OVERWRITE")
    conn.execute("UPDATE publication SET verified=1 WHERE request_id=?", (obj["request_id"],))
    conn.commit()
    return {"status": "PUBLISHED_VERIFIED", "request_id": obj["request_id"],
            "file_id": row["file_id"], "revision": row["seq"], "sha256": obj["sha256"],
            "name": row["name"], "url": "https://drive.google.com/file/d/" + row["file_id"] + "/view"}


def bootstrap():
    client = (CODE / "client.py").read_bytes()
    config = json.loads(read_private(STATE / "client-config.json"))
    return {"schema": 1, "client_base64": base64.b64encode(client).decode(),
            "client_sha256": sha(client), "config": config}


def main():
    os.umask(0o077)
    if os.getuid() != 10348 or str(Path.home()) != "/data/data/com.termux/files/home":
        raise PublishError("TERMUX_UID_REQUIRED")
    peer = os.environ.get("SSH_CONNECTION", "").split()
    if len(peer) != 4 or peer[0] not in {"127.0.0.1", "::1"} or peer[3] != "8023":
        raise PublishError("LOOPBACK_SSH_8023_REQUIRED")
    original = os.environ.get("SSH_ORIGINAL_COMMAND", "")
    if original == "mestry-publish-bootstrap-v1":
        return bootstrap()
    if original == "mestry-ui-code-v1":
        # Public, hash-pinned application code only; unavailable outside staging.
        update = CODE / "bridge-update.tar.gz"
        raw = read_private(update, limit=2000000)
        return {"schema": 1, "bundle_sha256": sha(raw),
                "bundle_base64": base64.b64encode(raw).decode("ascii")}
    if original == "mestry-drive-v1":
        # Same pinned SSH identity and loopback restriction. No arbitrary command.
        sys.path.insert(0, str(CODE))
        from drive_browser import main as browse_drive
        return browse_drive()
    if original != "mestry-publish-v1":
        raise PublishError("COMMAND_NOT_ALLOWED")
    obj, content = parse_request(sys.stdin.buffer.read(MAX_REQUEST + 1))
    read_config()
    with journal() as conn:
        return publish(Drive(), conn, obj, content)


if __name__ == "__main__":
    try:
        result = main()
    except PublishError as e:
        print(json.dumps({"status": "ERROR", "code": str(e)}))
        sys.exit(1)
    except Exception:
        # No tracebacks: OAuth/HTTP exceptions may carry secrets or document bytes.
        print(json.dumps({"status": "ERROR", "code": "LOCAL_ERROR_INSPECT_TERMUX_SETUP"}))
        sys.exit(1)
    print(json.dumps(result, ensure_ascii=False))

#!/usr/bin/env python3
"""Read-only Drive synchronization and durable, versioned text retrieval.

No OAuth setup, remote mutations, embeddings or external dependencies.
The caller supplies the already authorized Drive transport and account identity.
"""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import urllib.parse

from publisher import DriveError, PublishError, FOLDER_MIME, private_path, state_dir

META = "id,name,mimeType,parents,trashed,modifiedTime,size,version,md5Checksum"
MAX_BYTES = 65536
MAX_DOCUMENTS = 5000
MAX_CACHE_BYTES = 16 * 1024 * 1024


def checked_id(value):
    import re
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{10,100}", value):
        raise PublishError("SYNC_FILE_ID_INVALID")
    return value


def signature(meta):
    # version is mandatory for cache reuse; modifiedTime alone is insufficient.
    return json.dumps([meta.get(k) for k in ("version", "modifiedTime", "mimeType", "md5Checksum")],
                      separators=(",", ":"))


def transient(error):
    return (isinstance(error, DriveError) and (error.status == 429 or error.status >= 500)
            or type(error) in (OSError, TimeoutError)
            or isinstance(error, PublishError) and str(error).startswith(
                ("DRIVE_RESPONSE_UNKNOWN", "DRIVE_RESPONSE_INVALID_RETRY")))


class DriveAPI:
    """Bounded adapter over the installed publisher.Drive; GET requests only."""
    def __init__(self, drive, sleep=time.sleep, *, seconds=90):
        self.drive, self.sleep = drive, sleep
        self.deadline = time.monotonic() + seconds

    def call(self, route, **options):
        for attempt in range(3):
            if time.monotonic() >= self.deadline:
                raise PublishError("SYNC_TIME_BUDGET_REACHED")
            try:
                return self.drive.call(route, **options)
            except Exception as error:
                if not transient(error) or attempt == 2:
                    raise
                self.sleep((2 ** attempt) * (0.75 + os.urandom(1)[0] / 512))

    def metadata(self, value):
        value = checked_id(value)
        meta = self.call("files/" + value + "?" + urllib.parse.urlencode({"fields": META}))
        if meta.get("id") != value or type(meta.get("trashed")) is not bool:
            raise PublishError("SYNC_METADATA_INVALID")
        return meta

    def start(self):
        return self.call("changes/startPageToken")["startPageToken"]

    def children(self, folder, token):
        return self.call("files?" + urllib.parse.urlencode({
            "q": "'" + checked_id(folder) + "' in parents and trashed=false",
            "spaces": "drive", "pageSize": 50, "pageToken": token,
            "fields": "nextPageToken,incompleteSearch,files(" + META + ")"}))

    def changes(self, token):
        return self.call("changes?" + urllib.parse.urlencode({
            "pageToken": token, "pageSize": 50, "spaces": "drive",
            "includeRemoved": "true",
            "fields": "nextPageToken,newStartPageToken,changes(fileId,removed,file(" + META + "))"}))

    def content(self, meta):
        mime, value = meta["mimeType"], checked_id(meta["id"])
        if mime == "application/vnd.google-apps.document":
            route = "files/" + value + "/export?mimeType=text%2Fplain"
        elif mime.startswith("text/") or mime in {"application/json", "application/xml"}:
            route = "files/" + value + "?alt=media"
        else:
            return None
        data = self.call(route, media=True)
        if not isinstance(data, bytes) or len(data) > MAX_BYTES:
            raise PublishError("SYNC_CONTENT_TOO_LARGE")
        data.decode("utf-8")
        return data

    def member(self, value, root):
        first, current, seen = None, checked_id(value), set()
        for _ in range(33):
            if current in seen:
                break
            seen.add(current)
            try:
                meta = self.metadata(current)
            except DriveError as error:
                if error.status in (403, 404):
                    error.denied_id = current
                raise
            if meta.get("trashed"):
                error = PublishError("SYNC_DOCUMENT_UNAVAILABLE")
                error.denied_id = current
                raise error
            first = first or meta
            if current == root:
                if meta["mimeType"] != FOLDER_MIME:
                    break
                return first
            parents = meta.get("parents", [])
            if len(parents) != 1:
                break
            current = checked_id(parents[0])
        raise PublishError("SYNC_OUTSIDE_SELECTION")


class DocumentStore:
    """One account/root per DB; single writer and readers under the same lock."""
    def __init__(self, directory, account, root, *, clock=time.time):
        self.directory, self.root, self.clock = Path(directory), checked_id(root), clock
        state_dir(self.directory)
        self.lock_path = self.directory / "documents.lock"
        self.lock = None
        self.db = None
        self.account = hashlib.sha256(account.lower().encode()).hexdigest()

    def __enter__(self):
        fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, "a")
        try:
            private_path(self.lock_path)
            fcntl.flock(self.lock, fcntl.LOCK_EX)
            path = self.directory / "documents.sqlite3"
            if path.exists() or path.is_symlink():
                private_path(path)
            fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            os.close(fd)
            for suffix in ("-journal", "-wal", "-shm"):
                sidecar = Path(str(path) + suffix)
                if sidecar.exists() or sidecar.is_symlink():
                    private_path(sidecar)
            self.db = sqlite3.connect(path)
            self.db.row_factory = sqlite3.Row
            self.db.execute("PRAGMA synchronous=FULL")
            self.db.execute("PRAGMA secure_delete=ON")
            self.db.execute("PRAGMA journal_mode=DELETE")
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS nodes(id TEXT PRIMARY KEY, meta TEXT NOT NULL,
                    signature TEXT NOT NULL, status TEXT NOT NULL, digest TEXT,
                    seen INTEGER NOT NULL, checked REAL);
                CREATE TABLE IF NOT EXISTS objects(digest TEXT PRIMARY KEY, data BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS versions(id TEXT NOT NULL, signature TEXT NOT NULL,
                    meta TEXT NOT NULL, digest TEXT NOT NULL, captured REAL NOT NULL,
                    PRIMARY KEY(id,signature));
                CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, attempts INTEGER NOT NULL DEFAULT 0,
                    retry_at REAL NOT NULL DEFAULT 0, error TEXT);
                CREATE TABLE IF NOT EXISTS scans(id TEXT PRIMARY KEY, token TEXT NOT NULL, done INTEGER NOT NULL);
            """)
            identity = json.dumps([self.account, self.root, 1])
            if self.get("identity") not in (None, identity):
                raise PublishError("SYNC_STORE_IDENTITY_MISMATCH")
            with self.db:
                self.set("identity", identity)
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *args):
        if self.db is not None:
            self.db.close()
        if self.lock is not None:
            self.lock.close()

    def get(self, key):
        row = self.db.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    def set(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO config VALUES (?,?)", (key, str(value)))

    def unavailable(self, value):
        # Removed folder membership may affect descendants without their own changes.
        row = self.db.execute("SELECT meta FROM nodes WHERE id=?", (value,)).fetchone()
        folder = row and json.loads(row[0]).get("mimeType") == FOLDER_MIME
        # An unavailable unknown ancestor cannot leave other cached descendants exposed.
        if row is None:
            self.db.execute("UPDATE nodes SET status='pending' WHERE status='ready'")
            self.set("rescan", 1)
        self.db.execute("UPDATE nodes SET status='unavailable' WHERE id=?", (value,))
        self.db.execute("DELETE FROM jobs WHERE id=?", (value,))
        if value == self.root:
            self.set("blocked", 1)
        if folder or value == self.root:
            self.db.execute("UPDATE nodes SET status='pending' WHERE status='ready'")
            self.set("rescan", 1)

    def begin_scan(self, token=None):
        generation = int(self.get("generation") or 0) + 1
        self.set("generation", generation)
        self.set("scanning", 1)
        self.set("rescan", 0)
        if token is not None:
            self.set("cursor", token)
        self.db.execute("DELETE FROM scans")
        self.db.execute("INSERT INTO scans VALUES (?, '', 0)", (self.root,))
        # Do not expose stale descendants while membership is unresolved.
        self.db.execute("UPDATE nodes SET status='pending' WHERE status='ready'")

    def observe(self, meta):
        value = checked_id(meta.get("id"))
        old = self.db.execute("SELECT * FROM nodes WHERE id=?", (value,)).fetchone()
        sig = signature(meta)
        stable = old and old["signature"] == sig and meta.get("version") is not None
        status = "ready" if stable and old["digest"] else "pending"
        if meta.get("mimeType") == FOLDER_MIME:
            status = "folder"
        if meta.get("trashed"):
            status = "unavailable"
        self.db.execute("INSERT OR REPLACE INTO nodes VALUES (?,?,?,?,?,?,?)",
                        (value, json.dumps(meta), sig, status, old["digest"] if stable else None,
                         int(self.get("generation") or 0), self.clock() if stable else None))
        if status == "pending":
            self.db.execute("INSERT OR IGNORE INTO jobs(id) VALUES (?)", (value,))
        elif status in {"folder", "unavailable"}:
            self.db.execute("DELETE FROM jobs WHERE id=?", (value,))
        if self.db.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] > MAX_DOCUMENTS:
            raise PublishError("SYNC_DOCUMENT_LIMIT")

    def verify_root(self, api):
        allowed = getattr(getattr(api, "drive", None), "allowed_roots", None)
        if allowed is not None and self.root not in allowed:
            with self.db:
                self.set("blocked", 1)
            raise PublishError("READER_ROOT_NOT_SELECTED")
        try:
            root = api.metadata(self.root)
            if root["mimeType"] != FOLDER_MIME or root.get("trashed"):
                raise PublishError("SYNC_ROOT_UNAVAILABLE")
        except Exception as error:
            if not transient(error):
                with self.db:
                    self.set("blocked", 1)
                    self.unavailable(self.root)
            raise
        with self.db:
            if self.get("blocked") == "1":
                self.set("rescan", 1)
            self.set("blocked", 0)
            self.set("root_meta", json.dumps(root))
        return root

    def scan_page(self, api):
        task = self.db.execute("SELECT * FROM scans WHERE done=0 ORDER BY id LIMIT 1").fetchone()
        if not task:
            with self.db:
                self.db.execute("UPDATE nodes SET status='unavailable' WHERE seen!=?",
                                (int(self.get("generation")),))
                self.db.execute("DELETE FROM jobs WHERE id IN (SELECT id FROM nodes WHERE status='unavailable')")
                self.set("scanning", 0)
            return
        try:
            page = api.children(task["id"], task["token"])
        except DriveError as error:
            if error.status == 400 and task["token"]:
                with self.db:
                    self.db.execute("UPDATE scans SET token='' WHERE id=?", (task["id"],))
                raise PublishError("SYNC_INVENTORY_CURSOR_RESTARTED") from None
            raise
        if page.get("incompleteSearch") or not isinstance(page.get("files"), list):
            raise PublishError("SYNC_INCOMPLETE_INVENTORY")
        token = page.get("nextPageToken", "")
        if token and token == task["token"]:
            raise PublishError("SYNC_PAGINATION_STALLED")
        with self.db:
            for meta in page["files"]:
                if meta.get("parents") != [task["id"]] or meta.get("trashed") is not False:
                    raise PublishError("SYNC_INVENTORY_RESPONSE_INVALID")
                self.observe(meta)
                if meta["mimeType"] == FOLDER_MIME:
                    self.db.execute("INSERT OR IGNORE INTO scans VALUES (?, '', 0)", (meta["id"],))
            self.db.execute("UPDATE scans SET token=?,done=? WHERE id=?",
                            (token, int(not token), task["id"]))

    def change_page(self, api):
        cursor = self.get("cursor")
        try:
            page = api.changes(cursor)
        except DriveError as error:
            if error.status != 410:
                raise
            # Reconcile, retaining old objects; never infer mass deletion from 410.
            token = api.start()
            with self.db:
                self.begin_scan(token)
            return False
        token = page.get("nextPageToken") or page.get("newStartPageToken")
        if not isinstance(token, str) or not token or not isinstance(page.get("changes"), list):
            raise PublishError("SYNC_CHANGE_PAGE_INVALID")
        if page.get("nextPageToken") == cursor:
            raise PublishError("SYNC_PAGINATION_STALLED")
        with self.db:
            for change in page["changes"]:
                value = checked_id(change.get("fileId"))
                old = self.db.execute("SELECT meta FROM nodes WHERE id=?", (value,)).fetchone()
                meta = change.get("file")
                # The account-wide change feed can include unrelated documents.
                # Only selected/known items and direct children of known folders
                # enter the durable catalogue. Folder events reconcile descendants.
                related = old is not None or value == self.root
                if meta and not related:
                    for parent in meta.get("parents", []):
                        known = self.db.execute("SELECT status FROM nodes WHERE id=?", (parent,)).fetchone()
                        if parent == self.root or known and known["status"] == "folder":
                            related = True
                            break
                if not related:
                    continue
                folder = (meta and meta.get("mimeType") == FOLDER_MIME or
                          old and json.loads(old[0]).get("mimeType") == FOLDER_MIME)
                if change.get("removed") or meta and meta.get("trashed"):
                    self.unavailable(value)
                elif meta:
                    if meta.get("id") != value:
                        raise PublishError("SYNC_CHANGE_ID_MISMATCH")
                    # Membership must be revalidated by a job, even with same bytes.
                    self.observe(meta)
                    self.db.execute("UPDATE nodes SET status='pending' WHERE id=?", (value,))
                    self.db.execute("INSERT OR IGNORE INTO jobs(id) VALUES (?)", (value,))
                else:
                    raise PublishError("SYNC_CHANGE_WITHOUT_METADATA")
                if folder:
                    self.set("rescan", 1)
            # Durable receipt and invalidation are atomic with cursor advancement.
            self.set("cursor", token)
            if self.get("rescan") == "1":
                self.begin_scan()
        return not page.get("nextPageToken")

    def download(self, api, value):
        before = api.member(value, self.root)
        old = self.db.execute("SELECT * FROM nodes WHERE id=?", (value,)).fetchone()
        if before["mimeType"] == FOLDER_MIME:
            with self.db:
                self.observe(before)
            return
        sig = signature(before)
        with self.db:
            self.observe(before)
        if old and old["digest"] and old["signature"] == sig and before.get("version") is not None:
            row = self.db.execute("SELECT data FROM objects WHERE digest=?", (old["digest"],)).fetchone()
            if row and hashlib.sha256(row[0]).hexdigest() == old["digest"]:
                with self.db:
                    self.observe(before)
                    self.db.execute("DELETE FROM jobs WHERE id=?", (value,))
                return
        try:
            data = api.content(before)
        except (UnicodeError, PublishError) as error:
            if isinstance(error, PublishError) and str(error) not in {
                    "DRIVE_RESPONSE_TOO_LARGE", "SYNC_CONTENT_TOO_LARGE"}:
                raise
            data = None
        after = api.member(value, self.root)
        if signature(before) != signature(after) or before.get("parents") != after.get("parents"):
            with self.db:
                self.db.execute("UPDATE nodes SET status='pending' WHERE id=?", (value,))
            raise PublishError("SYNC_DOCUMENT_CHANGED_RETRY")
        with self.db:
            self.observe(after)
            if data is None:
                self.db.execute("UPDATE nodes SET status='external',digest=NULL,checked=? WHERE id=?", (self.clock(), value))
            else:
                digest = hashlib.sha256(data).hexdigest()
                used = self.db.execute("SELECT COALESCE(SUM(length(data)),0) FROM objects").fetchone()[0]
                exists = self.db.execute("SELECT 1 FROM objects WHERE digest=?", (digest,)).fetchone()
                if not exists and used + len(data) > MAX_CACHE_BYTES:
                    raise PublishError("SYNC_CACHE_BUDGET_EXCEEDED")
                self.db.execute("INSERT OR REPLACE INTO objects VALUES (?,?)", (digest, data))
                self.db.execute("INSERT OR IGNORE INTO versions VALUES (?,?,?,?,?)",
                                (value, sig, json.dumps(after), digest, self.clock()))
                self.db.execute("UPDATE nodes SET status='ready',digest=?,checked=? WHERE id=?",
                                (digest, self.clock(), value))
            self.db.execute("DELETE FROM jobs WHERE id=?", (value,))

    def drain(self, api, budget):
        for _ in range(budget):
            job = self.db.execute("SELECT * FROM jobs WHERE retry_at<=? ORDER BY id LIMIT 1",
                                  (self.clock(),)).fetchone()
            if not job:
                break
            try:
                self.download(api, job["id"])
            except Exception as error:
                if isinstance(error, PublishError) and str(error) == "SYNC_TIME_BUDGET_REACHED":
                    break  # No failed attempt: this batch simply has no execution time left.
                code = "SYNC_TRANSIENT_ERROR" if transient(error) else (
                    str(error) if isinstance(error, PublishError) else "SYNC_EXTRACTION_FAILED")
                with self.db:
                    if isinstance(error, DriveError) and error.status in (401, 403, 404):
                        self.unavailable(getattr(error, "denied_id", job["id"]))
                    elif isinstance(error, PublishError) and str(error) in {
                            "SYNC_OUTSIDE_SELECTION", "SYNC_DOCUMENT_UNAVAILABLE"}:
                        self.unavailable(getattr(error, "denied_id", job["id"]))
                    else:
                        delay = min(3600, 2 ** min(job["attempts"] + 1, 11))
                        self.db.execute("UPDATE jobs SET attempts=attempts+1,retry_at=?,error=? WHERE id=?",
                                        (self.clock() + delay, code, job["id"]))

    def sync(self, api, *, page_budget=50, job_budget=50):
        self.verify_root(api)
        with self.db:
            self.set("changes_complete", 0)
        if self.get("cursor") is None:
            token = api.start()  # Before inventory, to replay concurrent changes.
            with self.db:
                self.begin_scan(token)
        elif self.get("rescan") == "1":
            with self.db:
                self.begin_scan()
        complete = False
        for _ in range(page_budget):
            try:
                if self.get("scanning") == "1":
                    self.scan_page(api)
                elif self.change_page(api):
                    # A folder event can have started another scan in this page.
                    if self.get("scanning") != "1":
                        complete = True
                        break
            except PublishError as error:
                if str(error) != "SYNC_TIME_BUDGET_REACHED":
                    raise
                break
        if self.get("blocked") != "1":
            self.drain(api, job_budget)
        with self.db:
            self.set("changes_complete", int(complete and self.get("blocked") != "1"))
            if (complete and self.get("blocked") != "1" and self.get("rescan") != "1"
                    and self.get("scanning") != "1"
                    and not self.db.execute("SELECT 1 FROM jobs LIMIT 1").fetchone()):
                self.set("last_success", self.clock())
        return self.status()

    def status(self):
        return {"status": "OK", "scanning": self.get("scanning") == "1",
                "blocked": self.get("blocked") == "1",
                "reconciliation_required": self.get("rescan") == "1",
                "pending": self.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
                "ready": self.db.execute("SELECT COUNT(*) FROM nodes WHERE status='ready'").fetchone()[0],
                "changes_received": self.get("cursor") is not None,
                "changes_complete": self.get("changes_complete") == "1",
                "last_successful_sync_at": float(self.get("last_success") or 0) or None}

    def cached(self, value, *, offline=False):
        value = checked_id(value)
        if self.get("blocked") == "1":
            raise PublishError("SYNC_ACCESS_BLOCKED")
        row = self.db.execute("SELECT * FROM nodes WHERE id=?", (value,)).fetchone()
        if not row or row["status"] not in {"ready", "external"}:
            raise PublishError("SYNC_DOCUMENT_NOT_AVAILABLE")
        meta = json.loads(row["meta"])
        from drive_browser import public_file
        result = {"status": "OPEN_IN_DRIVE" if row["status"] == "external" else "OK",
                  "file": dict(public_file(meta), version=meta.get("version")),
                  "offline": offline, "freshness": "cached_unverified" if offline else "checked",
                  "checked_at": row["checked"], "sha256": row["digest"]}
        if row["status"] == "ready":
            blob = self.db.execute("SELECT data FROM objects WHERE digest=?", (row["digest"],)).fetchone()
            if not blob or hashlib.sha256(blob[0]).hexdigest() != row["digest"]:
                with self.db:
                    self.db.execute("UPDATE nodes SET status='pending' WHERE id=?", (value,))
                    self.db.execute("INSERT OR IGNORE INTO jobs(id) VALUES (?)", (value,))
                raise PublishError("SYNC_CACHE_CORRUPT")
            result["text"] = blob[0].decode("utf-8")
            if offline:
                result["text"] = "[COPIA LOCAL SIN VERIFICAR EN DRIVE; última comprobación: " + str(row["checked"]) + "]\n" + result["text"]
        return result

    def read(self, api, value, *, offline=False):
        value = checked_id(value)
        if offline:
            return self.cached(value, offline=True)
        try:
            self.verify_root(api)
            self.download(api, value)
        except Exception as error:
            if transient(error):
                return self.cached(value, offline=True)
            if (isinstance(error, DriveError) and error.status in (401, 403, 404)
                    or isinstance(error, PublishError) and str(error) in {
                        "SYNC_OUTSIDE_SELECTION", "SYNC_DOCUMENT_UNAVAILABLE"}):
                with self.db:
                    self.unavailable(getattr(error, "denied_id", value))
            raise
        return self.cached(value)

    def history(self, value):
        # Permission state and selection still apply to retained snapshots.
        self.cached(value, offline=True)
        rows = self.db.execute("SELECT meta,digest,captured FROM versions WHERE id=? ORDER BY captured DESC",
                               (checked_id(value),))
        return [{"version": json.loads(r["meta"]).get("version"),
                 "sha256": r["digest"], "captured_at": r["captured"]} for r in rows]

    def read_version(self, api, value, version, *, offline=False):
        if not offline:
            access = self.read(api, value)  # Revalidate access before exposing history.
            offline = access["offline"]
        self.cached(value, offline=True)
        rows = self.db.execute("SELECT * FROM versions WHERE id=? ORDER BY captured DESC",
                               (checked_id(value),))
        row = next((r for r in rows if json.loads(r["meta"]).get("version") == version), None)
        if row is None:
            raise PublishError("SYNC_VERSION_NOT_CACHED")
        blob = self.db.execute("SELECT data FROM objects WHERE digest=?", (row["digest"],)).fetchone()
        if not blob or hashlib.sha256(blob[0]).hexdigest() != row["digest"]:
            raise PublishError("SYNC_HISTORICAL_CACHE_CORRUPT")
        return {"status": "OK", "version": version, "sha256": row["digest"],
                "captured_at": row["captured"], "offline": offline,
                "freshness": "historical_snapshot",
                "text": "[VERSIÓN HISTÓRICA LOCAL; NO ES EL DOCUMENTO ACTUAL]\n" + blob[0].decode("utf-8")}

    def clear(self):
        """Explicit local-only cache reset; never delete a Drive original."""
        with self.db:
            for table in ("nodes", "objects", "versions", "jobs", "scans"):
                self.db.execute("DELETE FROM " + table)
            self.db.execute("DELETE FROM config WHERE key!='identity'")
        return self.status()

    def listing(self, folder):
        checked_id(folder)
        if self.get("blocked") == "1":
            raise PublishError("SYNC_ACCESS_BLOCKED")
        from drive_browser import public_file
        rows = self.db.execute("SELECT meta,status FROM nodes WHERE status IN ('ready','external','folder')")
        return [public_file(json.loads(row["meta"])) for row in rows
                if json.loads(row["meta"]).get("parents") == [folder]]


@contextlib.contextmanager
def selected_store(base, account, root):
    key = hashlib.sha256((account.lower() + "\0" + checked_id(root)).encode()).hexdigest()
    directory = Path(base) / "documents"
    state_dir(directory)
    with DocumentStore(directory / key, account, root) as store:
        yield store

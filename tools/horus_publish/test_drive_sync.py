import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from drive_sync import DocumentStore, DriveAPI
from publisher import DriveError, PublishError, FOLDER_MIME

ROOT, SUB, TEXT, OTHER = "root_folder_001", "child_folder_01", "document_text01", "other_folder_01"


def meta(value, mime=FOLDER_MIME, parent=None, version=1):
    return dict(id=value, name=value, mimeType=mime, parents=[parent] if parent else [],
                version=str(version), trashed=False, modifiedTime=str(version))


class API(DriveAPI):
    def __init__(self):
        self.items = {ROOT: meta(ROOT), SUB: meta(SUB, parent=ROOT),
                      TEXT: meta(TEXT, "text/markdown", SUB), OTHER: meta(OTHER)}
        self.data = {TEXT: b"first"}
        self.events, self.downloads, self.order = [], [], []
        self.fail, self.during_content, self.during_scan = None, None, None
        self.reject_token = False
        self.page_size = 2

    def metadata(self, value):
        if self.fail:
            raise self.fail
        if value not in self.items:
            raise DriveError(404)
        return copy.deepcopy(self.items[value])

    def start(self):
        self.order.append("start")
        return str(len(self.events))

    def children(self, folder, token):
        self.order.append("inventory")
        if self.fail:
            raise self.fail
        rows = sorted((m for m in self.items.values()
                       if m["parents"] == [folder] and not m["trashed"]), key=lambda m:m["id"])
        offset = int(token or 0)
        selected = copy.deepcopy(rows[offset:offset+self.page_size])
        if self.during_scan:
            callback, self.during_scan = self.during_scan, None
            callback()
        return dict(files=selected, nextPageToken=str(offset+self.page_size)
                    if offset+self.page_size < len(rows) else "")

    def changes(self, token):
        if self.reject_token:
            self.reject_token = False
            raise DriveError(410)
        offset = int(token)
        selected = copy.deepcopy(self.events[offset:offset+self.page_size])
        end = offset + len(selected)
        return dict(changes=selected, **({"nextPageToken": str(end)}
                    if end < len(self.events) else {"newStartPageToken": str(end)}))

    def content(self, item):
        self.downloads.append(item["id"])
        if self.fail:
            raise self.fail
        if item["mimeType"] not in {"text/markdown", "text/plain", "application/vnd.google-apps.document"}:
            return None
        value = self.data[item["id"]]
        if self.during_content:
            callback, self.during_content = self.during_content, None
            callback()
        return value

    def update(self, value, *, text=None, parent=None, trash=False):
        row = self.items[value]
        row["version"] = str(int(row["version"])+1)
        row["modifiedTime"] = row["version"]
        if parent:
            row["parents"] = [parent]
        row["trashed"] = trash
        if text is not None:
            self.data[value] = text
        self.events.append(dict(fileId=value, removed=False, file=copy.deepcopy(row)))

    def remove(self, value):
        self.items.pop(value)
        self.events.append(dict(fileId=value, removed=True))


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/"private"
        self.api = API()
        self.now = 1000.
        self.store = DocumentStore(self.path, "fixture@example.invalid", ROOT, clock=lambda:self.now).__enter__()

    def tearDown(self):
        self.store.__exit__()
        self.temp.cleanup()

    def reopen(self):
        self.store.__exit__()
        self.store = DocumentStore(self.path, "fixture@example.invalid", ROOT, clock=lambda:self.now).__enter__()

    def test_bootstrap_second_sync_and_read_do_not_download_again(self):
        self.store.sync(self.api)
        self.assertEqual(self.api.order[0], "start")
        self.assertEqual(self.api.downloads, [TEXT])
        self.store.sync(self.api)
        result = self.store.read(self.api, TEXT)
        self.assertEqual(result["text"], "first")
        self.assertEqual(self.api.downloads, [TEXT])
        self.assertEqual(result["freshness"], "checked")

    def test_changed_file_replaces_active_bytes_and_retains_old_object(self):
        self.store.sync(self.api)
        self.api.update(TEXT, text=b"second")
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "second")
        self.assertEqual(self.api.downloads, [TEXT, TEXT])
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM objects").fetchone()[0], 2)

    def test_resume_inventory_after_reopen(self):
        self.store.sync(self.api, page_budget=1, job_budget=0)
        self.assertTrue(self.store.status()["scanning"])
        self.reopen()
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "first")

    def test_change_during_bootstrap_is_replayed(self):
        self.api.during_scan = lambda:self.api.update(TEXT, text=b"edited during inventory")
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "edited during inventory")

    def test_page_receipt_survives_restart_before_download(self):
        self.store.sync(self.api)
        self.api.update(TEXT, text=b"after receipt")
        self.store.sync(self.api, job_budget=0)
        self.assertEqual(self.store.get("cursor"), "1")
        with self.assertRaises(PublishError):
            self.store.cached(TEXT, offline=True)
        self.reopen()
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "after receipt")

    def test_edit_during_download_is_not_served_as_current(self):
        self.api.during_content = lambda:self.api.update(TEXT, text=b"racing")
        self.store.sync(self.api)
        with self.assertRaises(PublishError):
            self.store.cached(TEXT)
        self.assertEqual(self.store.status()["pending"], 1)
        self.now += 10
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "racing")

    def test_deleted_document_is_unavailable_offline(self):
        self.store.sync(self.api)
        self.api.remove(TEXT)
        self.store.sync(self.api)
        with self.assertRaises(PublishError):
            self.store.read(self.api, TEXT, offline=True)

    def test_move_out_of_selection_invalidates(self):
        self.store.sync(self.api)
        self.api.update(TEXT, parent=OTHER)
        self.store.sync(self.api)
        with self.assertRaises(PublishError):
            self.store.cached(TEXT)

    def test_folder_move_invalidates_descendant_without_child_event(self):
        self.store.sync(self.api)
        self.api.update(SUB, parent=OTHER)
        self.store.sync(self.api)
        with self.assertRaises(PublishError):
            self.store.cached(TEXT, offline=True)

    def test_folder_move_into_selection_discovers_existing_children(self):
        self.api.items[SUB]["parents"] = [OTHER]
        self.store.sync(self.api)
        self.assertFalse(self.api.downloads)
        self.api.update(SUB, parent=ROOT)
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "first")

    def test_410_reconciles_without_erasing_objects(self):
        self.store.sync(self.api)
        self.api.reject_token = True
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "first")
        self.assertEqual(len(self.api.downloads), 1)

    def test_revoked_root_blocks_all_offline_access(self):
        self.store.sync(self.api)
        del self.api.items[ROOT]
        with self.assertRaises(DriveError):
            self.store.sync(self.api)
        self.reopen()
        with self.assertRaisesRegex(PublishError, "BLOCKED"):
            self.store.cached(TEXT, offline=True)

    def test_transient_read_returns_explicit_offline_copy(self):
        self.store.sync(self.api)
        self.api.fail = DriveError(503)
        value = self.store.read(self.api, TEXT)
        self.assertTrue(value["offline"])
        self.assertEqual(value["freshness"], "cached_unverified")
        self.assertTrue(value["text"].startswith("[COPIA LOCAL SIN VERIFICAR"))
        self.assertEqual(value["sha256"], hashlib.sha256(b"first").hexdigest())

    def test_permission_error_does_not_fall_back_to_cache(self):
        self.store.sync(self.api)
        self.api.fail = DriveError(403)
        with self.assertRaises(DriveError):
            self.store.read(self.api, TEXT)
        with self.assertRaises(PublishError):
            self.store.cached(TEXT, offline=True)

    def test_corrupt_blob_is_repaired_on_next_online_read(self):
        self.store.sync(self.api)
        with self.store.db:
            self.store.db.execute("UPDATE objects SET data=?", (b"corrupt",))
        with self.assertRaisesRegex(PublishError, "CORRUPT"):
            self.store.cached(TEXT)
        self.assertEqual(self.store.read(self.api, TEXT)["text"], "first")
        self.assertEqual(len(self.api.downloads), 2)

    def test_failure_during_inventory_never_generates_mass_deletion(self):
        self.store.sync(self.api)
        with self.store.db:
            self.store.begin_scan()
        self.api.fail = DriveError(503)
        with self.assertRaises(DriveError):
            self.store.sync(self.api)
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM objects").fetchone()[0], 1)
        self.api.fail = None
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "first")

    def test_selection_and_account_identity_cannot_be_reused(self):
        self.store.__exit__()
        with self.assertRaisesRegex(PublishError, "IDENTITY"):
            with DocumentStore(self.path, "another@example.invalid", ROOT):
                pass
        self.store = DocumentStore(self.path, "fixture@example.invalid", ROOT).__enter__()

    def test_private_permissions_and_symlink_rejection(self):
        self.assertEqual((self.path/"documents.sqlite3").stat().st_mode & 0o777, 0o600)
        target = self.path/"bad"
        target.symlink_to(self.path, target_is_directory=True)
        with self.assertRaises(PublishError):
            with DocumentStore(target, "fixture@example.invalid", ROOT):
                pass

    def test_http_retry_is_bounded_and_does_not_retry_permissions(self):
        class FailingTransport:
            def __init__(self, status): self.calls,self.status = 0,status
            def call(self,*args,**kwargs):
                self.calls += 1
                raise DriveError(self.status)
        for status,count in [(429,3),(503,3),(403,1),(401,1)]:
            drive = FailingTransport(status)
            with self.assertRaises(DriveError): DriveAPI(drive,sleep=lambda _:None).call("files")
            self.assertEqual(drive.calls,count)

    def test_multi_page_changes_are_all_processed(self):
        self.store.sync(self.api)
        for n in range(5):
            value = "new_document_%03d" % n
            self.api.items[value] = meta(value, "text/markdown", ROOT)
            self.api.data[value] = str(n).encode()
            self.api.update(value)
        self.store.sync(self.api)
        self.assertEqual(self.store.status()["ready"], 6)
        self.assertEqual(self.store.get("cursor"), "5")

    def test_unsupported_format_is_external_not_empty_text(self):
        self.api.items[TEXT]["mimeType"] = "application/pdf"
        self.store.sync(self.api)
        value = self.store.cached(TEXT)
        self.assertEqual(value["status"], "OPEN_IN_DRIVE")
        self.assertNotIn("text", value)

    def test_retry_job_is_durable_with_backoff(self):
        original = self.api.content
        self.api.content = lambda _: (_ for _ in ()).throw(DriveError(503))
        self.store.sync(self.api)
        row = self.store.db.execute("SELECT * FROM jobs").fetchone()
        self.assertGreater(row["retry_at"], self.now)
        self.reopen()
        self.api.content = original
        self.now += 10
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"], "first")


    def test_change_page_rolls_back_receipt_and_invalidations_together(self):
        self.store.sync(self.api)
        self.api.update(TEXT,text=b"new")
        self.api.events.append(dict(fileId="invalid",removed=True))
        with self.assertRaises(PublishError):
            self.store.sync(self.api)
        self.assertEqual(self.store.get("cursor"),"0")
        self.assertEqual(self.store.cached(TEXT)["text"],"first")

    def test_unknown_offline_document_fails_without_fabricating_content(self):
        with self.assertRaisesRegex(PublishError,"NOT_AVAILABLE"):
            self.store.read(None,TEXT,offline=True)

    def test_size_limit_is_external_and_cache_budget_is_visible(self):
        from unittest.mock import patch
        self.api.content=lambda _: (_ for _ in ()).throw(PublishError("SYNC_CONTENT_TOO_LARGE"))
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["status"],"OPEN_IN_DRIVE")
        self.api.content=lambda _: b"real text"
        self.api.update(TEXT,text=b"real text")
        with patch("drive_sync.MAX_CACHE_BYTES",1):
            self.store.sync(self.api)
        with self.assertRaises(PublishError):
            self.store.cached(TEXT)
        job=self.store.db.execute("SELECT error FROM jobs").fetchone()
        self.assertEqual(job["error"],"SYNC_CACHE_BUDGET_EXCEEDED")

    def test_http_time_budget_stops_before_another_request(self):
        class Never:
            def call(self,*args,**kwargs):
                raise AssertionError("network must not be called")
        with self.assertRaisesRegex(PublishError,"TIME_BUDGET"):
            DriveAPI(Never(),seconds=0).call("files")


    def test_clear_removes_only_derived_local_data_and_allows_rebootstrap(self):
        self.store.sync(self.api)
        original=copy.deepcopy(self.api.items)
        value=self.store.clear()
        self.assertEqual(value["ready"],0)
        self.assertIsNone(self.store.get("cursor"))
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM objects").fetchone()[0],0)
        self.assertEqual(self.api.items,original)
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"],"first")



    def test_history_retrieves_old_snapshot_without_replacing_current(self):
        self.store.sync(self.api)
        self.now += 1
        self.api.update(TEXT,text=b"second")
        self.store.sync(self.api)
        history=self.store.history(TEXT)
        self.assertEqual({v["version"] for v in history},{"1","2"})
        old=self.store.read_version(self.api,TEXT,"1")
        self.assertEqual(old["freshness"],"historical_snapshot")
        self.assertTrue(old["text"].endswith("first"))
        self.assertEqual(self.store.cached(TEXT)["text"],"second")
        self.api.remove(TEXT)
        self.store.sync(self.api)
        with self.assertRaises(PublishError):
            self.store.read_version(None,TEXT,"1",offline=True)

    def test_revoked_ancestor_invalidates_cached_siblings_without_change_poll(self):
        sibling="sibling_text_01"
        self.api.items[sibling]=meta(sibling,"text/markdown",SUB)
        self.api.data[sibling]=b"sibling"
        self.store.sync(self.api)
        del self.api.items[SUB]
        with self.assertRaises(DriveError):
            self.store.read(self.api,TEXT)
        with self.assertRaises(PublishError):
            self.store.read(None,sibling,offline=True)
        self.assertTrue(self.store.status()["reconciliation_required"])

    def test_unrelated_account_changes_do_not_enter_selected_catalogue(self):
        self.store.sync(self.api)
        outside="outside_text_01"
        self.api.items[outside]=meta(outside,"text/markdown",OTHER)
        self.api.data[outside]=b"private unrelated"
        self.api.update(outside)
        self.api.events.append(dict(fileId="removed_other_01",removed=True))
        self.store.sync(self.api)
        self.assertIsNone(self.store.db.execute("SELECT id FROM nodes WHERE id=?",(outside,)).fetchone())
        self.assertFalse(self.store.status()["reconciliation_required"])
        self.assertEqual(self.store.get("cursor"),"2")
        self.assertEqual(self.api.downloads,[TEXT])

    def test_batch_time_budget_does_not_penalize_unstarted_jobs(self):
        self.store.sync(self.api,job_budget=0)
        original=self.api.content
        self.api.content=lambda _: (_ for _ in ()).throw(PublishError("SYNC_TIME_BUDGET_REACHED"))
        self.store.drain(self.api,40)
        job=self.store.db.execute("SELECT * FROM jobs").fetchone()
        self.assertEqual(job["attempts"],0)
        self.assertEqual(job["retry_at"],0)
        self.assertIsNone(job["error"])
        self.api.content=original
        self.store.sync(self.api)
        self.assertEqual(self.store.cached(TEXT)["text"],"first")


class Transport:
    def __init__(self, api):
        self.api = api

    def call(self, route, **options):
        import urllib.parse
        url = urllib.parse.urlsplit(route)
        query = urllib.parse.parse_qs(url.query, keep_blank_values=True)
        if options.get("media"):
            return self.api.content(self.api.metadata(url.path.split("/")[1]))
        if url.path == "changes/startPageToken":
            return {"startPageToken": self.api.start()}
        if url.path == "changes":
            return self.api.changes(query["pageToken"][0])
        if url.path.startswith("files/"):
            return self.api.metadata(url.path.split("/")[1])
        if url.path == "files":
            return self.api.children(query["q"][0].split("'")[1], query.get("pageToken", [""])[0])
        raise AssertionError("unexpected route")


class CachedBrowserTests(unittest.TestCase):
    def setUp(self):
        import drive_browser
        self.temp = tempfile.TemporaryDirectory()
        self.api = API()
        self.transport = Transport(self.api)
        self.state = {"schema":1,"enabled":[ROOT],"assignments":{drive_browser.PROJECT:ROOT}}

    def tearDown(self):
        self.temp.cleanup()

    def call(self, op, drive=True, **fields):
        import drive_browser
        request = drive_browser.parse_request(json.dumps(dict(schema=1,op=op,root_id=ROOT,**fields)).encode())
        return drive_browser.cached_handle(self.transport if drive else None, self.state, request,
                                           lambda _:None, base=Path(self.temp.name), account="fixture@example.invalid")

    def test_existing_wire_contract_reuses_cache_and_reads_offline_after_reopen(self):
        self.call("list", folder_id=ROOT, page_token="")
        self.assertEqual(self.call("read", file_id=TEXT)["text"], "first")
        self.assertEqual(self.call("read", file_id=TEXT)["text"], "first")
        self.assertEqual(len(self.api.downloads),1)
        self.assertTrue(self.call("read", drive=False, file_id=TEXT)["offline"])

    def test_disabled_selection_cannot_read_previous_cache(self):
        self.call("read", file_id=TEXT)
        self.state["enabled"] = []
        with self.assertRaisesRegex(PublishError,"DISABLED"):
            self.call("read", drive=False, file_id=TEXT)

    def test_offline_listing_signals_staleness_to_existing_ui(self):
        self.call("list", folder_id=ROOT, page_token="")
        value=self.call("list",drive=False,folder_id=SUB,page_token="")
        self.assertTrue(value["offline"])
        self.assertTrue(value["files"][0]["name"].startswith("[Copia local sin verificar]"))

    def test_observed_revocation_blocks_later_offline_read(self):
        self.call("list", folder_id=ROOT, page_token="")
        del self.api.items[ROOT]
        with self.assertRaises(PublishError):
            self.call("list",folder_id=ROOT,page_token="")
        with self.assertRaisesRegex(PublishError,"BLOCKED"):
            self.call("read",drive=False,file_id=TEXT)


if __name__ == "__main__":
    unittest.main()

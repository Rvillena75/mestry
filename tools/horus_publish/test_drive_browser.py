import copy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
import urllib.parse

import drive_browser as browser
from publisher import DriveError, FOLDER_MIME, PublishError

ROOT, SUB, OTHER, TEXT, DOC, IMAGE = ("folder_root_001", "folder_child_01", "folder_other_01", "text_document_1", "google_document", "image_document1")


def meta(value, name, mime=FOLDER_MIME, parents=None):
    return {"id": value, "name": name, "mimeType": mime, "parents": parents or [], "trashed": False}


class FakeDrive:
    def __init__(self):
        self.items = {ROOT: meta(ROOT, "Proyecto"), SUB: meta(SUB, "Subcarpeta", parents=[ROOT]),
                      OTHER: meta(OTHER, "Otra"), TEXT: meta(TEXT, "nota.md", "text/markdown", [SUB]),
                      DOC: meta(DOC, "Documento", "application/vnd.google-apps.document", [ROOT]),
                      IMAGE: meta(IMAGE, "imagen.png", "image/png", [ROOT])}
        self.calls = []
        self.list_extra = []
        self.content = b"# MESTRY\nDocumento de prueba\n"
        self.next_page = ""

    def call(self, route, **options):
        self.calls.append((route, options))
        if options.get("media"):
            return self.content
        url = urllib.parse.urlsplit(route)
        if url.path.startswith("files/"):
            value = url.path.split("/")[1]
            if value not in self.items:
                raise DriveError(404)
            return copy.deepcopy(self.items[value])
        query = urllib.parse.parse_qs(url.query)["q"][0]
        if " in parents" in query:
            parent = query.split("'")[1]
            rows = [v for v in self.items.values() if v["parents"] == [parent]] + self.list_extra
        else:
            rows = [v for v in self.items.values() if v["mimeType"] == FOLDER_MIME]
        return {"files": copy.deepcopy(rows), "nextPageToken": self.next_page}


class DriveBrowserTests(unittest.TestCase):
    def setUp(self):
        self.drive = FakeDrive()
        self.state = {"schema": 1, "enabled": [ROOT], "assignments": {browser.PROJECT: ROOT}}
        self.saved = []

    def request(self, op, **fields):
        return browser.parse_request(json.dumps(dict(schema=1, op=op, **fields)).encode())

    def run_op(self, op, **fields):
        return browser.handle(self.drive, self.state, self.request(op, **fields), lambda v: self.saved.append(copy.deepcopy(v)))

    def test_state_distinguishes_google_visibility_and_app_enabled_list(self):
        result = self.run_op("state")
        self.assertEqual({f["id"] for f in result["folders"] if f["enabled"]}, {ROOT})
        self.assertEqual(len(result["folders"]), 3)
        self.assertEqual(result["assignments"][0]["folder"]["id"], ROOT)
        self.assertEqual(self.saved, [])

    def test_disable_is_local_and_removes_project_assignment(self):
        self.run_op("folder.enable", folder_id=ROOT, enabled=False)
        self.assertEqual(self.state["enabled"], [])
        self.assertEqual(self.state["assignments"], {})
        with self.assertRaisesRegex(PublishError, "DISABLED"):
            self.run_op("list", root_id=ROOT, folder_id=ROOT, page_token="")
        self.assertTrue(all(not opts for _, opts in self.drive.calls))

    def test_enable_then_assign_other_already_granted_folder(self):
        self.run_op("folder.enable", folder_id=OTHER, enabled=True)
        result = self.run_op("assign", project=browser.PROJECT, folder_id=OTHER)
        self.assertEqual(result["assignments"][0]["folder"]["id"], OTHER)
        self.assertEqual(len(self.saved), 2)

    def test_assignment_cannot_implicitly_enable_a_folder(self):
        with self.assertRaisesRegex(PublishError, "DISABLED"):
            self.run_op("assign", project=browser.PROJECT, folder_id=OTHER)
        self.assertFalse(self.saved)

    def test_remove_assignment_keeps_folder_and_documents(self):
        self.run_op("assign", project=browser.PROJECT, folder_id=None)
        self.assertEqual(self.state["enabled"], [ROOT])
        self.assertFalse(self.state["assignments"])

    def test_nested_folder_and_text_preview(self):
        result = self.run_op("list", root_id=ROOT, folder_id=SUB, page_token="")
        self.assertEqual([f["id"] for f in result["files"]], [TEXT])
        preview = self.run_op("read", root_id=ROOT, file_id=TEXT)
        self.assertEqual(preview["text"], self.drive.content.decode())

    def test_list_excludes_wrong_parent_in_api_response(self):
        self.drive.list_extra = [self.drive.items[OTHER], dict(self.drive.items[TEXT], trashed=True)]
        result = self.run_op("list", root_id=ROOT, folder_id=SUB, page_token="")
        self.assertEqual([f["id"] for f in result["files"]], [TEXT])

    def test_sibling_outside_enabled_root_is_rejected(self):
        with self.assertRaisesRegex(PublishError, "OUTSIDE"):
            self.run_op("list", root_id=ROOT, folder_id=OTHER, page_token="")

    def test_parent_cycle_fails_closed(self):
        self.drive.items[SUB]["parents"] = [SUB]
        with self.assertRaisesRegex(PublishError, "OUTSIDE"):
            self.run_op("read", root_id=ROOT, file_id=TEXT)

    def test_revoked_root_blocks_descendant_even_if_file_remains_accessible(self):
        del self.drive.items[ROOT]
        with self.assertRaisesRegex(PublishError, "NOT_GRANTED_OR_UNAVAILABLE"):
            self.run_op("read", root_id=ROOT, file_id=TEXT)

    def test_unavailable_root_can_still_be_disabled_by_user(self):
        del self.drive.items[ROOT]
        value = self.run_op("state")
        root = next(row for row in value["folders"] if row["id"] == ROOT)
        self.assertFalse(root["available"])
        self.assertTrue(root["enabled"])
        self.assertFalse(value["assignments"][0]["folder"]["available"])
        self.run_op("folder.enable", folder_id=ROOT, enabled=False)
        self.assertNotIn(ROOT, self.state["enabled"])
        self.assertFalse(self.state["assignments"])

    def test_ungranted_folder_cannot_be_enabled_by_pasting_id(self):
        with self.assertRaisesRegex(PublishError, "NOT_GRANTED_OR_UNAVAILABLE"):
            self.run_op("folder.enable", folder_id="ungranted_folder", enabled=True)
        self.assertFalse(self.saved)

    def test_files_are_not_accepted_as_roots(self):
        with self.assertRaisesRegex(PublishError, "FOLDER_REQUIRED"):
            self.run_op("folder.enable", folder_id=TEXT, enabled=True)

    def test_google_document_is_exported_as_plain_text(self):
        self.assertEqual(self.run_op("read", root_id=ROOT, file_id=DOC)["status"], "OK")
        self.assertTrue(any("/export?mimeType=text%2Fplain" in path for path, _ in self.drive.calls))

    def test_binary_file_opens_in_drive_without_download(self):
        self.assertEqual(self.run_op("read", root_id=ROOT, file_id=IMAGE)["status"], "OPEN_IN_DRIVE")
        self.assertFalse(any(options.get("media") for _, options in self.drive.calls))

    def test_api_urls_are_constructed_from_validated_ids(self):
        value = browser.public_file(dict(self.drive.items[TEXT], webViewLink="javascript:alert(1)"))
        self.assertEqual(value["url"], "https://drive.google.com/file/d/" + TEXT + "/view")

    def test_pagination_is_explicit(self):
        self.drive.next_page = "opaque-token"
        result = self.run_op("list", root_id=ROOT, folder_id=SUB, page_token="previous+token")
        self.assertEqual(result["next_page_token"], "opaque-token")
        self.assertTrue(any("pageToken=previous%2Btoken" in path for path, _ in self.drive.calls))

    def test_rejects_extra_fields_duplicate_keys_and_bool_schema(self):
        for raw in [b'{"schema":1,"op":"state","command":"whoami"}',
                    b'{"schema":1,"op":"state","op":"read"}',
                    b'{"schema":true,"op":"state"}']:
            with self.subTest(raw=raw), self.assertRaises(PublishError): browser.parse_request(raw)

    def test_rejects_shell_query_and_foreign_project_inputs(self):
        for value in ["root' or trashed=false", "../../token.json", "$(whoami)", ""]:
            with self.subTest(value=value), self.assertRaises(PublishError): self.request("folder.enable", folder_id=value, enabled=True)
        with self.assertRaises(PublishError): self.request("assign", project="/home/horus", folder_id=ROOT)
        with self.assertRaises(PublishError): self.request("folder.enable", folder_id=ROOT, enabled="true")

    def test_default_state_does_not_write_publisher_journal(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp); db = path / "journal.sqlite3"
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE folder(singleton INTEGER, file_id TEXT)")
                conn.execute("INSERT INTO folder VALUES (1, ?)", (ROOT,))
            os.chmod(db, 0o600)
            before = hashlib.sha256(db.read_bytes()).hexdigest()
            self.assertEqual(browser.load_state(path), self.state)
            self.assertEqual(hashlib.sha256(db.read_bytes()).hexdigest(), before)
            self.assertFalse((path / "drive-browser.json").exists())


if __name__ == "__main__": unittest.main()

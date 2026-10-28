import base64
import ast
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
import subprocess
from unittest.mock import patch

import client
import oauth_setup
import publisher as p


class FakeDrive:
    def __init__(self):
        self.files = {}
        self.bodies = {}
        self.generated = 0
        self.creates = []
        self.email = p.ACCOUNT
        self.lose_next_response = False
        self.corrupt_next_body = False

    def account(self):
        return self.email

    def generate_id(self):
        self.generated += 1
        return f"file_{self.generated:012d}"

    def metadata(self, file_id):
        if file_id not in self.files:
            raise p.DriveError(404)
        return copy.deepcopy(self.files[file_id])

    def create(self, metadata, content=None):
        file_id = metadata["id"]
        if file_id in self.files:
            raise p.DriveError(409)
        self.creates.append(file_id)
        self.files[file_id] = dict(copy.deepcopy(metadata), trashed=False, ownedByMe=True,
                                  owners=[{"emailAddress": p.ACCOUNT}],
                                  permissions=[{"type": "user", "role": "owner", "emailAddress": p.ACCOUNT}])
        self.bodies[file_id] = b"unexpected remote edit" if self.corrupt_next_body else content
        self.corrupt_next_body = False
        if self.lose_next_response:
            self.lose_next_response = False
            raise p.PublishError("DRIVE_RESPONSE_UNKNOWN_RETRY_SAME_CONTENT")
        return {"id": file_id}

    def download(self, file_id):
        return self.bodies[file_id]


class RequestTests(unittest.TestCase):
    def parse(self, value):
        return p.parse_request(json.dumps(value).encode())

    def test_utf8_crlf_preserved_exactly(self):
        raw = "# Revisión\r\nSí: español\r\n".encode()
        obj, data = self.parse(client.make_request(raw))
        self.assertEqual(data, raw)
        self.assertEqual(obj["sha256"], p.sha(raw))

    def test_reject_paths_unknown_fields_wrong_schema(self):
        cases = [{"document": "../S23_PUBLISH_TEST.md"}, {"destination": "somewhere"},
                 {"schema": True}, {"sha256": "0" * 64}, {"request_id": "0" * 64},
                 {"content_base64": "!!not base64!!"}, {"content_base64": 123}]
        for fields in cases:
            with self.subTest(fields=fields), self.assertRaises(p.PublishError):
                self.parse(dict(client.make_request(b"ok\n"), **fields))

    def test_reject_duplicate_json_keys(self):
        raw = json.dumps(client.make_request(b"ok\n"))[:-1] + ',"schema":1}'
        with self.assertRaisesRegex(p.PublishError, "DUPLICATE_JSON_KEY"):
            p.parse_request(raw.encode())

    def test_reject_binary_empty_and_oversize(self):
        for raw in (b"", b"a\0b", b"a\x1bb", b"\xff", b"x" * 65537):
            with self.subTest(size=len(raw)), self.assertRaises(p.PublishError):
                self.parse(client.make_request(raw))
        with self.assertRaisesRegex(p.PublishError, "REQUEST_TOO_LARGE"):
            p.parse_request(b"x" * 90001)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.context = p.journal(Path(self.temp.name))
        self.db = self.context.__enter__()
        self.drive = FakeDrive()
        folder = p.prepare_folder(self.drive, self.db)
        self.folder = folder["folder_id"]
        self.drive.files[self.folder]["parents"] = [p.REVIEW_ID]

    def tearDown(self):
        self.context.__exit__(None, None, None)
        self.temp.cleanup()

    def publish(self, data=b"# Prueba\n"):
        request = client.make_request(data)
        request, raw = p.parse_request(json.dumps(request).encode())
        return p.publish(self.drive, self.db, request, raw, day="2026-10-21")

    def test_new_file_roundtrip_and_repeat_deduplicated(self):
        one = self.publish()
        two = self.publish()
        self.assertEqual(one, two)
        self.assertEqual(one["revision"], 1)
        self.assertEqual(len(self.drive.creates), 2)  # folder plus one MD
        self.assertEqual(self.drive.bodies[one["file_id"]], b"# Prueba\n")

    def test_lost_upload_response_reuses_reserved_id_after_reopen(self):
        self.drive.lose_next_response = True
        with self.assertRaisesRegex(p.PublishError, "UNKNOWN"):
            self.publish()
        reserved = dict(self.db.execute("SELECT * FROM publication").fetchone())
        self.assertEqual(reserved["verified"], 0)
        # Simulate a new SSH process with a fresh SQLite connection.
        self.context.__exit__(None, None, None)
        self.context = p.journal(Path(self.temp.name))
        self.db = self.context.__enter__()
        done = self.publish()
        self.assertEqual(done["file_id"], reserved["file_id"])
        self.assertEqual(self.drive.generated, 2)
        self.assertEqual(len(self.drive.creates), 2)

    def test_human_edit_survives_new_revision(self):
        first = self.publish()
        self.drive.bodies[first["file_id"]] += b"human edit\n"
        second = self.publish(b"new revision\n")
        self.assertEqual(second["revision"], 2)
        self.assertNotEqual(first["file_id"], second["file_id"])
        self.assertEqual(self.drive.bodies[first["file_id"]], b"# Prueba\nhuman edit\n")

    def test_retry_human_edited_file_fails_without_overwrite(self):
        first = self.publish()
        self.drive.bodies[first["file_id"]] = b"human edit\n"
        with self.assertRaisesRegex(p.PublishError, "REMOTE_CONTENT_CHANGED_NO_OVERWRITE"):
            self.publish()
        self.assertEqual(self.drive.bodies[first["file_id"]], b"human edit\n")
        self.assertEqual(len(self.drive.creates), 2)

    def test_deleted_verified_file_never_recreated(self):
        first = self.publish()
        del self.drive.files[first["file_id"]]
        with self.assertRaises(p.DriveError):
            self.publish()
        self.assertEqual(len(self.drive.creates), 2)

    def test_wrong_readback_does_not_claim_success(self):
        self.drive.corrupt_next_body = True
        with self.assertRaisesRegex(p.PublishError, "REMOTE_CONTENT_CHANGED"):
            self.publish()
        self.assertEqual(self.db.execute("SELECT verified FROM publication").fetchone()[0], 0)

    def test_non_private_folder_prevents_reservation_or_upload(self):
        self.drive.files[self.folder]["permissions"].append({"type": "anyone", "role": "reader"})
        with self.assertRaisesRegex(p.PublishError, "DRIVE_NOT_PRIVATE"):
            self.publish()
        self.assertEqual(self.drive.generated, 1)

    def test_wrong_account_prevents_reservation_or_upload(self):
        self.drive.email = "another@example.com"
        with self.assertRaisesRegex(p.PublishError, "DRIVE_ACCOUNT_MISMATCH"):
            self.publish()
        self.assertEqual(self.drive.generated, 1)

    def test_folder_must_be_under_existing_review(self):
        self.drive.files[self.folder]["parents"] = ["some-other-parent"]
        with self.assertRaisesRegex(p.PublishError, "MOVE_TO_REVIEW_REQUIRED"):
            self.publish()
        self.assertEqual(self.drive.generated, 1)

    def test_file_metadata_and_permissions_checked_after_upload(self):
        first = self.publish()
        self.drive.files[first["file_id"]]["parents"] = ["wrong-folder"]
        with self.assertRaisesRegex(p.PublishError, "REMOTE_METADATA_CHANGED"):
            self.publish()
        self.drive.files[first["file_id"]]["parents"] = [self.folder]
        self.drive.files[first["file_id"]]["permissions"].append({"type": "anyone", "role": "reader"})
        with self.assertRaisesRegex(p.PublishError, "DRIVE_NOT_PRIVATE"):
            self.publish()

    def test_daily_quota_blocks_new_but_allows_retry(self):
        for n in range(20):
            self.publish(f"{n}\n".encode())
        with self.assertRaisesRegex(p.PublishError, "PILOT_QUOTA_REACHED"):
            self.publish(b"21\n")
        self.assertEqual(self.publish(b"0\n")["revision"], 1)

    def test_folder_creation_lost_response_reconciles_same_id(self):
        with tempfile.TemporaryDirectory() as td, p.journal(Path(td)) as conn:
            fake = FakeDrive()
            fake.lose_next_response = True
            with self.assertRaises(p.PublishError):
                p.prepare_folder(fake, conn)
            result = p.prepare_folder(fake, conn)
            self.assertEqual(result["status"], "MOVE_FOLDER_TO_REVIEW_REQUIRED")
            self.assertEqual(fake.generated, 1)
            self.assertEqual(len(fake.creates), 1)


class LocalBoundaryTests(unittest.TestCase):
    def test_client_rejects_symlink_traversal_and_fifo(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            dest = root / p.DOCUMENT
            other = root / "other"
            other.write_text("hello\n")
            dest.symlink_to(other)
            with self.assertRaises(OSError):
                client.read_document(root, p.DOCUMENT)
            dest.unlink()
            os.mkfifo(dest)
            with self.assertRaisesRegex(ValueError, "REGULAR_FILE_REQUIRED"):
                client.read_document(root, p.DOCUMENT)
            with self.assertRaises(ValueError):
                client.read_document(root, "../other")

    def test_private_storage_rejects_symlink_and_open_permissions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dest = root / "token.json"
            p.write_private(dest, b'not-a-real-token')
            self.assertEqual(dest.stat().st_mode & 0o777, 0o600)
            dest.chmod(0o644)
            with self.assertRaises(p.PublishError):
                p.read_private(dest)
            dest.unlink()
            dest.symlink_to(root / "other")
            with self.assertRaises(p.PublishError):
                p.write_private(dest, b'anything')
            self.assertFalse((root / "other").exists())

    def test_client_validation_fixed_google_endpoints(self):
        value = {"installed": {"client_id": "fake.apps.googleusercontent.com", "client_secret": "synthetic",
                  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                  "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": ["http://localhost"]}}
        self.assertEqual(oauth_setup.validate_client(json.dumps(value)), value)
        value["installed"]["token_uri"] = "https://untrusted.example/token"
        with self.assertRaises(p.PublishError):
            oauth_setup.validate_client(json.dumps(value))

    def test_callback_cannot_start_without_explicit_flag(self):
        with self.assertRaisesRegex(p.PublishError, "EXPLICIT_APPROVAL"):
            oauth_setup.authorize(False, {})

    def test_ssh_capability_fixed_and_forwardings_disabled(self):
        args = client.ssh_args("mestry-publish-v1")
        self.assertIn("StrictHostKeyChecking=yes", args)
        self.assertIn("ClearAllForwardings=yes", args)
        self.assertIn("IdentityAgent=none", args)
        self.assertEqual(args[-2:], ["u0_a348@127.0.0.1", "mestry-publish-v1"])

    @unittest.skipUnless((Path(__file__).parent / "install.py").is_file(), "WSL-only installer")
    def test_generated_bootstrap_is_valid_and_pins_configured_host_key(self):
        import install
        # Public fixture only: the test must not depend on a personal SSH pin.
        blob = bytes.fromhex("0000000b7373682d6564323535313900000020") + bytes(range(32))
        host_key = "ssh-ed25519 " + base64.b64encode(blob).decode()
        digest = base64.b64encode(__import__('hashlib').sha256(blob).digest()).decode().rstrip("=")
        fingerprint = "SHA256:" + digest
        with patch.object(install, "HOST_KEY", host_key), patch.object(install, "HOST_FP", fingerprint):
            body = install.bootstrap_script()
        py = body.split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY\n", 1)[0]
        ast.parse(py)
        subprocess.run(["sh", "-n"], input=body.encode(), check=True, capture_output=True)
        self.assertIn("[127.0.0.1]:8023 " + host_key, body)
        self.assertIn(fingerprint, body)


class NativeRefreshTests(unittest.TestCase):
    def test_refresh_uses_post_fixed_google_endpoint_and_saves_privately(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            original = {"token": "old-synthetic-token", "refresh_token": "synthetic-refresh",
                        "client_id": "fake.apps.googleusercontent.com", "client_secret": "synthetic-secret",
                        "token_uri": "https://oauth2.googleapis.com/token", "scopes": [p.SCOPE],
                        "expiry": "2000-01-01T00:00:00Z"}
            p.write_private(path / "token.json", json.dumps(original).encode())
            seen = []

            class Response:
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def read(self, limit):
                    return json.dumps({"access_token": "new-synthetic-token", "expires_in": 3600,
                                       "token_type": "Bearer", "scope": p.SCOPE}).encode()

            class Opener:
                def open(self, req, timeout):
                    seen.append(req)
                    return Response()

            with patch.object(p.urllib.request, "build_opener", return_value=Opener()):
                result = p.Drive(path)
            self.assertEqual(result.creds.token, "new-synthetic-token")
            self.assertEqual(json.loads(p.read_private(path / "token.json"))["token"], result.creds.token)
            self.assertEqual((path / "token.json").stat().st_mode & 0o777, 0o600)
            self.assertEqual(seen[0].full_url, "https://oauth2.googleapis.com/token")
            self.assertEqual(seen[0].method, "POST")
            self.assertIn(b"grant_type=refresh_token", seen[0].data)
            self.assertNotIn("synthetic", seen[0].full_url)

    def test_refresh_scope_expansion_fails_without_replacing_saved_token(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            original = {"token": "old-synthetic-token", "refresh_token": "synthetic-refresh",
                        "client_id": "fake", "client_secret": "synthetic-secret",
                        "token_uri": "https://oauth2.googleapis.com/token", "scopes": [p.SCOPE]}
            raw = json.dumps(original).encode()
            p.write_private(path / "token.json", raw)

            class Response:
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def read(self, limit):
                    return json.dumps({"access_token": "new", "expires_in": 3600,
                                       "token_type": "Bearer", "scope": "https://www.googleapis.com/auth/drive"}).encode()

            class Opener:
                def open(self, req, timeout): return Response()

            with patch.object(p.urllib.request, "build_opener", return_value=Opener()):
                with self.assertRaisesRegex(p.PublishError, "OAUTH_SCOPE_MISMATCH"):
                    p.Drive(path)
            self.assertEqual(p.read_private(path / "token.json"), raw)

    def test_broad_stored_scope_rejected_before_http(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            p.write_private(path / "token.json", json.dumps({"scopes": [p.SCOPE, "broad"]}).encode())
            with patch.object(p.urllib.request, "build_opener") as opener:
                with self.assertRaisesRegex(p.PublishError, "OAUTH_SCOPE_MISMATCH"):
                    p.Drive(path)
                opener.assert_not_called()

    def test_bearer_redirects_not_followed(self):
        self.assertIsNone(p.NoRedirect().redirect_request(None, None, 302, "", {}, "https://untrusted.example"))


if __name__ == "__main__":
    unittest.main()

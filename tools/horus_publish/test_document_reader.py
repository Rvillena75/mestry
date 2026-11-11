import copy
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import document_reader as reader
import authorize_reader_wsl as helper
from publisher import Drive, PublishError, SCOPE, FOLDER_MIME, write_private

ROOT = "selected_root_01"


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.client = dict(client_id="fixture.apps.googleusercontent.com", client_secret="fixture-only",
                           token_uri="https://oauth2.googleapis.com/token",
                           auth_uri="https://accounts.google.com/o/oauth2/auth", redirect_uris=["http://localhost"])
        self.token = dict(self.client, scopes=[reader.READER_SCOPE], token="fixture-access",
                          refresh_token="fixture-refresh", expiry="2999-01-01T00:00:00+00:00")
        self.writer = dict(self.token, scopes=[SCOPE])
        write_private(self.base/"client.json", json.dumps({"installed":self.client}).encode())
        write_private(self.base/"token.json", json.dumps(self.writer).encode())
        import drive_browser
        state=dict(schema=1, enabled=[ROOT], assignments={drive_browser.PROJECT:ROOT})
        write_private(self.base/"drive-browser.json", json.dumps(state).encode())

    def activate(self):
        write_private(self.base/"reader/selection.json", json.dumps(dict(schema=1,roots=[ROOT])).encode())
        write_private(self.base/"reader/token.json", json.dumps(self.token).encode())

    def test_separate_reader_token_does_not_replace_publisher(self):
        self.activate()
        before=(self.base/"token.json").read_bytes()
        drive=reader.open_reader(self.base)
        self.assertIsInstance(drive,reader.ReaderDrive)
        self.assertEqual(drive.allowed_roots,[ROOT])
        self.assertEqual(before,(self.base/"token.json").read_bytes())
        from drive_sync import DriveAPI, DocumentStore
        with DocumentStore(self.base/"outside-store",reader.ACCOUNT,"outside_root_01") as store:
            with self.assertRaisesRegex(PublishError,"ROOT_NOT_SELECTED"):
                store.verify_root(DriveAPI(drive))

    def test_missing_marker_preserves_old_reader_and_malformed_marker_fails_closed(self):
        with patch.object(reader,"Drive",return_value="old") as old:
            self.assertEqual(reader.open_reader(self.base),"old")
            old.assert_called_once_with(self.base)
        write_private(self.base/"reader/selection.json",b'{}')
        with self.assertRaises(PublishError):reader.open_reader(self.base)

    def test_broader_scope_or_wrong_client_is_rejected(self):
        for token in [dict(self.token,scopes=[SCOPE,reader.READER_SCOPE]),
                      dict(self.token,client_id="other.apps.googleusercontent.com")]:
            with self.assertRaises(PublishError):reader.validate_token(token,self.client)

    def test_readonly_transport_rejects_writes_before_http(self):
        self.activate()
        drive=reader.ReaderDrive(self.base)
        for route,options in [("files",dict(method="POST")),("files/"+ROOT,dict(method="PATCH")),
                              ("files/generateIds",{}),("https://example.invalid/files",{}),
                              ("files",dict(upload=True)),("files",dict(data=b"x"))]:
            with self.assertRaises(PublishError):drive.call(route,**options)
        with patch.object(Drive,"call",return_value={"fixture":True}) as call:
            self.assertEqual(drive.call("files/"+ROOT+"?fields=id"),{"fixture":True})
            call.assert_called_once()

    def test_state_only_exposes_selected_root_and_does_not_list_account_folders(self):
        from drive_browser import state_response, handle
        from test_drive_browser import FakeDrive, ROOT as existing_root, OTHER
        drive=FakeDrive();drive.allowed_roots=[existing_root]
        state=dict(schema=1,enabled=[existing_root],assignments={})
        value=state_response(drive,state)
        self.assertEqual([row["id"] for row in value["folders"]],[existing_root])
        self.assertFalse(any(route.startswith("files?") for route,_ in drive.calls))
        state["enabled"].append(OTHER)
        from drive_browser import cached_handle
        with self.assertRaisesRegex(PublishError,"ROOT_NOT_SELECTED"):
            cached_handle(drive,state,dict(op="read",root_id=OTHER,file_id=OTHER),
                          lambda _:None,base=self.base)
        with self.assertRaisesRegex(PublishError,"NOT_SELECTED"):
            handle(drive,state,dict(op="folder.enable",folder_id=OTHER,enabled=True),lambda _:None)

    def commit(self, token=None, roots=None):
        return reader.commit_authorization(dict(token=token or self.token, roots=roots or [ROOT]),self.base)

    def test_native_commit_verifies_both_grants_and_forces_new_inventory(self):
        before=(self.base/"token.json").read_bytes()
        with patch.object(Drive,"refresh",return_value=self.writer), \
             patch.object(reader.ReaderDrive,"refresh",return_value=self.token), \
             patch.object(reader,"require_account") as account, \
             patch("drive_sync.DriveAPI.metadata",return_value=dict(id=ROOT,trashed=False,mimeType=FOLDER_MIME)):
            value=self.commit()
        self.assertEqual(value["status"],"READER_AUTHORIZED")
        self.assertEqual(account.call_count,2)
        self.assertEqual(before,(self.base/"token.json").read_bytes())
        from drive_sync import selected_store
        with selected_store(self.base,reader.ACCOUNT,ROOT) as store:
            self.assertTrue(store.status()["reconciliation_required"])

    def test_selection_change_and_scope_expansion_never_activate_reader(self):
        with self.assertRaises(PublishError):self.commit(roots=["different_root1"])
        with self.assertRaises(PublishError):self.commit(token=dict(self.token,scopes=[SCOPE,reader.READER_SCOPE]))
        self.assertFalse((self.base/"reader/selection.json").exists())

    def test_account_or_writer_failure_keeps_tokens_and_marker_unchanged(self):
        before=(self.base/"token.json").read_bytes()
        with patch.object(Drive,"refresh",side_effect=PublishError("WRITER_REFRESH_FAILED")):
            with self.assertRaises(PublishError):self.commit()
        self.assertFalse((self.base/"reader/selection.json").exists())
        self.assertEqual(before,(self.base/"token.json").read_bytes())

    def test_second_consent_is_not_started_automatically(self):
        self.activate()
        with self.assertRaisesRegex(PublishError,"ALREADY_CONFIGURED"):
            reader.prepare_authorization(self.base)


class HelperTests(unittest.TestCase):
    def test_callback_flag_is_required_before_any_ssh_or_browser(self):
        with patch.object(sys,"argv",["helper"]),patch.object(helper,"remote") as remote:
            with self.assertRaisesRegex(ValueError,"APPROVAL"):
                helper.main()
            remote.assert_not_called()

    def test_oauth_uses_pkce_exact_readonly_scope_and_existing_callback(self):
        token=dict(scopes=[helper.SCOPE],refresh_token="fixture")
        creds=types.SimpleNamespace(refresh_token="fixture",to_json=lambda:json.dumps(token))
        flow=types.SimpleNamespace(oauth2session=types.SimpleNamespace(token=dict(scope=helper.SCOPE)))
        factory=unittest.mock.Mock()
        factory.from_client_config.return_value=flow
        flow.run_local_server=unittest.mock.Mock(return_value=creds)
        sdk=types.ModuleType("google_auth_oauthlib.flow");sdk.InstalledAppFlow=factory
        with patch.dict(sys.modules,{"google_auth_oauthlib.flow":sdk}):
            self.assertEqual(helper.authorize({"installed":{}},"fixture@example.invalid"),token)
            self.assertEqual(factory.from_client_config.call_args.args[1],[helper.SCOPE])
            self.assertTrue(factory.from_client_config.call_args.kwargs["autogenerate_code_verifier"])
            self.assertEqual(flow.run_local_server.call_args.kwargs["port"],53682)
            self.assertEqual(flow.run_local_server.call_args.kwargs["include_granted_scopes"],"false")
            flow.oauth2session.token["scope"]=helper.SCOPE+" "+SCOPE
            with self.assertRaises(ValueError):helper.authorize({"installed":{}},"fixture@example.invalid")

    def test_missing_callback_has_safe_actionable_error_without_token_details(self):
        flow=types.SimpleNamespace(oauth2session=types.SimpleNamespace(token={}))
        factory=unittest.mock.Mock()
        factory.from_client_config.return_value=flow
        flow.run_local_server=unittest.mock.Mock(return_value=None)
        sdk=types.ModuleType("google_auth_oauthlib.flow");sdk.InstalledAppFlow=factory
        with patch.dict(sys.modules,{"google_auth_oauthlib.flow":sdk}):
            with self.assertRaisesRegex(ValueError,"CONSENT_NOT_COMPLETED"):
                helper.authorize({"installed":{}},"fixture@example.invalid")
            flow.run_local_server.side_effect=Warning("synthetic private information")
            with self.assertRaisesRegex(ValueError,"GOOGLE_SCOPE_DIFFERENT"):
                helper.authorize({"installed":{}},"fixture@example.invalid")

    def test_remote_helper_program_compiles_without_running_it(self):
        compile(helper.REMOTE,"remote-reader-helper","exec")


if __name__=="__main__":
    unittest.main()

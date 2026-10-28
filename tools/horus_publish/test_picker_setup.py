import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import authorize_picker_wsl as setup
from publisher import ACCOUNT, PublishError, SCOPE


class PickerSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.client = Path(self.temp.name) / 'desktop-fixture.json'
        self.client.write_text(json.dumps({'installed': {
            'client_id': 'synthetic.apps.googleusercontent.com', 'client_secret': 'fixture-only',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token', 'redirect_uris': ['http://localhost']}}))
        self.creds = types.SimpleNamespace(refresh_token='synthetic-refresh', to_json=lambda: json.dumps({'scopes': [SCOPE], 'refresh_token': 'synthetic-refresh'}))
        self.flow = types.SimpleNamespace(oauth2session=types.SimpleNamespace(token={'scope': SCOPE}))
        self.factory = unittest.mock.Mock()
        self.factory.from_client_config.return_value = self.flow
        self.flow.run_local_server = unittest.mock.Mock(return_value=self.creds)
        self.remote = unittest.mock.Mock(return_value={'status': 'PICKER_AUTHORIZATION_SAVED'})

    def run_setup(self, extra=None, account=ACCOUNT):
        argv = ['picker', str(self.client), '--folder-id', 'fixture_folder_01'] + (['--allow-loopback-53682'] if extra is None else extra)
        sdk = types.ModuleType('google_auth_oauthlib.flow');sdk.InstalledAppFlow = self.factory
        with patch.object(sys, 'argv', argv), patch.dict(sys.modules, {'google_auth_oauthlib.flow': sdk}), \
             patch.object(setup, 'remote', self.remote), patch.object(setup.Drive, 'account', return_value=account), \
             patch.object(setup.logging, 'disable'), contextlib.redirect_stdout(io.StringIO()):
            return setup.main()

    def test_same_scope_pkce_fixed_callback_and_picker_folder(self):
        self.run_setup()
        self.assertEqual(self.factory.from_client_config.call_args.args[1], [SCOPE])
        self.assertTrue(self.factory.from_client_config.call_args.kwargs['autogenerate_code_verifier'])
        options = self.flow.run_local_server.call_args.kwargs
        self.assertEqual((options['host'], options['port'], options['timeout_seconds']), ('127.0.0.1', 53682, 180))
        self.assertEqual(options['trigger_onepick'], 'true')
        self.assertEqual(options['allow_folder_selection'], 'true')
        self.assertEqual(options['file_ids'], 'fixture_folder_01')
        self.assertEqual([call.args[0]['action'] for call in self.remote.call_args_list], ['backup', 'commit'])

    def test_existing_callback_approval_flag_required_before_network(self):
        with self.assertRaisesRegex(PublishError, 'CALLBACK_APPROVAL'):
            self.run_setup(extra=[])
        self.remote.assert_not_called()
        self.factory.from_client_config.assert_not_called()

    def test_expanded_scope_is_rejected_without_token_commit(self):
        self.flow.oauth2session.token['scope'] = SCOPE + ' https://www.googleapis.com/auth/drive.readonly'
        with self.assertRaisesRegex(PublishError, 'SCOPE_OR_REFRESH'):
            self.run_setup()
        self.assertEqual(self.remote.call_count, 1)

    def test_missing_refresh_token_is_rejected_without_commit(self):
        self.creds.refresh_token = None
        with self.assertRaisesRegex(PublishError, 'SCOPE_OR_REFRESH'):
            self.run_setup()
        self.assertEqual(self.remote.call_count, 1)

    def test_cancel_keeps_active_token_and_does_not_expose_exception(self):
        self.flow.run_local_server.side_effect = RuntimeError('synthetic sensitive response')
        with self.assertRaisesRegex(PublishError, '^PICKER_NOT_COMPLETED_PREVIOUS_TOKEN_PRESERVED$'):
            self.run_setup()
        self.assertEqual(self.remote.call_count, 1)

    def test_wrong_account_does_not_commit(self):
        with self.assertRaisesRegex(PublishError, 'ACCOUNT_MISMATCH'):
            self.run_setup(account='other@example.invalid')
        self.assertEqual(self.remote.call_count, 1)

    def test_ssh_failure_is_sanitized_and_token_is_not_in_argv(self):
        fake = types.SimpleNamespace(stdout=b'non-json synthetic private response', returncode=1)
        with patch.object(setup.subprocess, 'run', return_value=fake) as run:
            with self.assertRaisesRegex(PublishError, '^PRIVATE_PICKER_SSH_FAILED_NO_SECRET_DETAILS$'):
                setup.remote({'token': 'synthetic-private-value'})
        self.assertNotIn('synthetic-private-value', str(run.call_args.args))
        self.assertIn(b'synthetic-private-value', run.call_args.kwargs['input'])

    def test_native_commit_program_compiles_without_running_it(self):
        compile(setup.REMOTE, '<native-picker-commit>', 'exec')


if __name__ == '__main__': unittest.main()

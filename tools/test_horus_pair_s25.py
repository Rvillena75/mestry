"""Offline checks of the pairing helper's credential and authorization boundaries."""
import base64
from contextlib import ExitStack, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import horus_pair_s25 as pair


class PairingBoundaries(unittest.TestCase):
    def test_password_is_stdin_and_never_in_wsl_arguments(self):
        secret = 'offline-test-only-$(`quoted`)\ncon-acento-á'
        request = {'password': secret, 'keyType': 'ssh-ed25519', 'keyData': 'public'}
        response = 'Result: Bundle[{json={"status":"incorrect"}}]\r\n'
        with patch.object(pair.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, response, '')) as run:
            result = pair.provider('7', 'pair', request)
        argv = run.call_args.args[0]
        encoded = run.call_args.kwargs['input'].strip()
        self.assertNotIn(secret, ' '.join(argv))
        self.assertNotIn(encoded, ' '.join(argv))
        self.assertEqual(json.loads(base64.b64decode(encoded)), request)
        self.assertIn('--arg "$mestry_pair_request"', argv[-1])
        self.assertEqual(result, {'status': 'incorrect'})

    def test_raw_provider_failure_does_not_reveal_the_payload(self):
        secret = 'OFFLINE_SENTINEL_DO_NOT_PRINT'
        with self.assertRaises(pair.PairError) as error:
            pair.parse_provider('Provider error; request=' + secret)
        self.assertNotIn(secret, str(error.exception))

    def test_provider_response_excludes_unexpected_secret_fields(self):
        response = 'Result: Bundle[{json={"status":"ok","password":"sentinel","extra":"private"}}]'
        self.assertEqual(pair.parse_provider(response), {'status': 'ok'})

    def test_subprocess_failure_does_not_include_stdin_or_stderr(self):
        failure = subprocess.CompletedProcess([], 1, 'sentinel stdout', 'sentinel stderr')
        with patch.object(pair.subprocess, 'run', return_value=failure):
            with self.assertRaises(pair.PairError) as error:
                pair.invoke(['adb.exe'], body='sentinel input')
        self.assertNotIn('sentinel', str(error.exception))

    def test_ambiguous_device_is_rejected(self):
        devices = ('List of devices attached\n'
                   'one device model:SM_S918B transport_id:1\n'
                   'two device model:SM_S918B transport_id:2\n')
        with patch.object(pair, 'invoke', return_value=devices):
            with self.assertRaises(pair.PairError):
                pair.transport()

    def test_changed_public_key_is_rejected(self):
        blob = b'\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20' + b'\0' * 32
        key = 'ssh-ed25519 ' + base64.b64encode(blob).decode() + ' mestry-s25\n'
        with patch.object(pair, 'invoke', side_effect=['port 8023\nstricthostkeychecking true\n', key]):
            with self.assertRaises(pair.PairError):
                pair.public_key()

    def execute_fake(self, responses, *, check=False, tty=True):
        report = {}
        output = io.StringIO()
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(pair, 'transport', return_value='7'))
        stack.enter_context(patch.object(pair, 'public_key', return_value={
            'keyType': 'ssh-ed25519', 'keyData': 'public', 'label': 'mestry-s25'}))
        provider = stack.enter_context(patch.object(pair, 'provider', side_effect=responses))
        prompt = stack.enter_context(patch.object(pair.getpass, 'getpass', return_value='OFFLINE_PASSWORD_SENTINEL'))
        stack.enter_context(patch.object(pair.sys.stdin, 'isatty', return_value=tty))
        stack.enter_context(redirect_stdout(output))
        return report, output, provider, prompt, lambda: pair.execute(report, check=check)

    @staticmethod
    def before(**changes):
        return {'status': 'ok', 'configured': True, 'appVersion': '1.0.4',
                'port': 8022, 'username': 'horus', 'authorized': False, **changes}

    def test_check_mode_never_prompts_or_pairs(self):
        report, _, provider, prompt, execute = self.execute_fake([self.before()], check=True)
        execute()
        self.assertEqual(report['status'], 'PREFLIGHT_PASS')
        prompt.assert_not_called()
        self.assertEqual([call.args[1] for call in provider.call_args_list], ['status'])

    def test_existing_pairing_is_not_repeated(self):
        report, _, provider, prompt, execute = self.execute_fake([self.before(authorized=True)])
        execute()
        self.assertEqual(report['status'], 'ALREADY_AUTHORIZED')
        prompt.assert_not_called()
        self.assertEqual(provider.call_count, 1)

    def test_version_drift_stops_before_password(self):
        _, _, provider, prompt, execute = self.execute_fake([self.before(appVersion='changed')])
        with self.assertRaises(pair.PairError):
            execute()
        prompt.assert_not_called()
        self.assertEqual(provider.call_count, 1)

    def test_noninteractive_terminal_cannot_supply_password(self):
        _, _, provider, prompt, execute = self.execute_fake([self.before()], tty=False)
        with self.assertRaises(pair.PairError):
            execute()
        prompt.assert_not_called()
        self.assertEqual(provider.call_count, 1)

    def test_incorrect_password_is_one_attempt_and_not_saved(self):
        report, output, provider, prompt, execute = self.execute_fake([
            self.before(), {'status': 'incorrect'}])
        with self.assertRaises(pair.PairError):
            execute()
        self.assertEqual([call.args[1] for call in provider.call_args_list], ['status', 'pair'])
        self.assertEqual(prompt.call_count, 1)
        self.assertNotIn('OFFLINE_PASSWORD_SENTINEL', json.dumps(report) + output.getvalue())

    def test_success_requires_matching_fingerprint_and_postcheck(self):
        report, output, provider, _, execute = self.execute_fake([
            self.before(), {'status': 'ok', 'fingerprint': pair.S25_FP, 'started': True},
            self.before(authorized=True, state='starting', enabled=True)])
        execute()
        self.assertEqual(report['status'], 'PAIRED_VERIFIED')
        self.assertEqual([call.args[1] for call in provider.call_args_list], ['status', 'pair', 'status'])
        self.assertNotIn('OFFLINE_PASSWORD_SENTINEL', json.dumps(report) + output.getvalue())

    def test_postcheck_cannot_turn_missing_authorization_into_success(self):
        report, _, _, _, execute = self.execute_fake([
            self.before(), {'status': 'ok', 'fingerprint': pair.S25_FP}, self.before()])
        with self.assertRaises(pair.PairError):
            execute()
        self.assertNotEqual(report.get('status'), 'PAIRED_VERIFIED')


if __name__ == '__main__':
    unittest.main()

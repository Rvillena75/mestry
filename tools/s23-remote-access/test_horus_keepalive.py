"""Recovery must fail closed when bridge ownership cannot be established."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import horus_keepalive as keepalive


class OwnershipGateTests(unittest.TestCase):
    def test_failed_status_does_not_request_a_restart(self):
        failed = subprocess.CompletedProcess([], 1, stdout='', stderr='private diagnostic')
        with patch.object(keepalive.subprocess, 'run', return_value=failed) as run:
            with self.assertRaisesRegex(ValueError, '^CONTROLLER_STATUS_FAILED$'):
                keepalive.recover(lambda: False, keepalive.controller)
        self.assertEqual([call.args[0][-1] for call in run.call_args_list], ['status'])

    def test_missing_or_non_boolean_ownership_is_rejected(self):
        for value in [None, 0, 'false']:
            with self.subTest(value=value):
                response = subprocess.CompletedProcess([], 0, stdout=json.dumps({
                    'marker': 'MESTRY_BRIDGE_STATUS', 'owned_process_running': value,
                }))
                with patch.object(keepalive.subprocess, 'run', return_value=response):
                    with self.assertRaisesRegex(ValueError, '^CONTROLLER_STATUS_INVALID$'):
                        keepalive.controller('status')

    def test_live_owned_bridge_is_never_restarted(self):
        calls = []
        def control(action):
            calls.append(action)
            return True
        self.assertEqual(keepalive.recover(lambda: False, control), 'degraded_owned_process')
        self.assertEqual(calls, ['status'])

    def test_restart_requires_explicit_absence(self):
        calls = []
        health = iter([False, True])
        def control(action):
            calls.append(action)
            return action == 'start'
        self.assertEqual(keepalive.recover(lambda: next(health), control), 'recovered')
        self.assertEqual(calls, ['status', 'start'])


class ProjectPollTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name)
        self.patcher = patch.object(keepalive, 'STATE', self.state)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def config(self, mode=0o600):
        root = self.state / 'project'
        (root / 'tools').mkdir(parents=True)
        (root / 'tools/work_session.py').write_text('# fixture runner\n')
        config = self.state / 'projects.json'
        config.write_text(json.dumps({'schema': 1, 'projects': [str(root)]}))
        config.chmod(mode)

    def test_absent_config_keeps_original_worker_behavior(self):
        with patch.object(keepalive.subprocess, 'run') as run:
            self.assertIsNone(keepalive.poll_projects())
            run.assert_not_called()

    def test_insecure_config_never_invokes_runner(self):
        self.config(0o644)
        with patch.object(keepalive.subprocess, 'run') as run:
            self.assertEqual(keepalive.poll_projects()['state'], 'project_poll_failed_no_private_details')
            run.assert_not_called()

    def test_success_fetches_only_and_reports_pending_version(self):
        self.config()
        result = subprocess.CompletedProcess([], 0, stdout=json.dumps({
            'state': 'OK', 'fetch_only': True, 'head': 'a' * 40, 'remote': 'b' * 40}))
        with patch.object(keepalive.subprocess, 'run', return_value=result) as run:
            value = keepalive.poll_projects()
        self.assertEqual(run.call_args.args[0][-2:], ['receive', '--fetch-only'])
        self.assertTrue(value['projects'][0]['update_pending'])

    def test_busy_is_deferred_without_any_apply_command(self):
        self.config()
        result = subprocess.CompletedProcess([], 3, stdout=json.dumps({'state': 'BLOCKED', 'reason': 'BUSY'}))
        with patch.object(keepalive.subprocess, 'run', return_value=result):
            self.assertEqual(keepalive.poll_projects()['projects'][0]['state'], 'deferred')


if __name__ == '__main__':
    unittest.main()

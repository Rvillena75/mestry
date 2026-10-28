"""Recovery must fail closed when bridge ownership cannot be established."""
import json
import subprocess
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


if __name__ == '__main__':
    unittest.main()

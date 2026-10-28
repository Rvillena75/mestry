"""Local fixtures only; no phone, credentials, model or real SSH connection."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location('mestry_' + name, HERE / (name + '.py'))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


class HelperTests(unittest.TestCase):
    def test_private_pairing_write_and_stale_process_refusal(self):
        control = module('horus_control')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'synthetic-value'
            control.write_private(path, 'PUBLIC TEST FIXTURE ONLY')
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            control.PID = Path(temp) / 'process.json'
            control.PID.write_text(json.dumps({'pid': os.getpid(), 'start_time': 'wrong-start-time'}))
            self.assertIsNone(control.owned_process(Path(sys.executable)))
            control.PID.write_text(json.dumps({'pid': '../not-a-pid', 'start_time': 'invalid'}))
            self.assertIsNone(control.owned_process(Path(sys.executable)))

    def test_install_refuses_wrong_profile_before_writing(self):
        installer = module('horus_install')
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)
            with self.assertRaisesRegex(ValueError, 'HORUS_SSH_PROFILE_REQUIRED'):
                installer.install(source)
            self.assertEqual(list(source.iterdir()), [])

    def test_upgrade_checks_hashes_and_tracks_unfinished_turns(self):
        updater = module('horus_upgrade')
        self.assertEqual(updater.active_turns({'sessions': {'s': {'events': [
            {'event': 'turn/started', 'turn_id': 'a'}, {'event': 'turn/started', 'turn_id': 'b'},
            {'event': 'turn/completed', 'turn_id': 'a'}]}}}), 1)
        self.assertEqual(updater.active_turns({'sessions': {'s': {'events': [
            {'event': 'turn/started', 'turn_id': 'a'}, {'event': 'turn/completed', 'turn_id': 'a'}]}}}), 0)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'fixture.txt').write_text('code only')
            import hashlib
            manifest = json.dumps({'files': {'fixture.txt': hashlib.sha256(b'code only').hexdigest()}}).encode()
            (root / 'manifest.json').write_bytes(manifest)
            self.assertEqual(updater.verify_release(root), manifest)
            (root / 'fixture.txt').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'HASH_MISMATCH'):
                updater.verify_release(root)
            with self.assertRaisesRegex(ValueError, 'HORUS_SSH_PROFILE_REQUIRED'):
                updater.upgrade(root)

    def test_staging_serves_only_fixed_code_artifact_and_closes_on_stop(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            bundle = temp / 'public-code.tar.gz'
            bundle.write_bytes(b'PUBLIC CODE FIXTURE ONLY')
            result = temp / 'result.json'
            fake = temp / 'fake-ssh.py'
            fake.write_text('import sys,time,json\nif "-N" in sys.argv: time.sleep(30)\nelse: print(json.dumps({"uid":10348,"port":"8023","gatewayports":"no","allowtcpforwarding":"yes"}))\n')
            runner = temp / 'runner.py'
            runner.write_text(
                'import importlib.util,sys\n'
                f's=importlib.util.spec_from_file_location("fixture_stage",{str(HERE / "stage_horus.py")!r})\n'
                'm=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n'
                f'm.SSH=[sys.executable,{str(fake)!r}]\n'
                f'm.stage(m.Path({str(bundle)!r}),m.Path({str(result)!r}),30)\n')
            process = subprocess.Popen([sys.executable, '-B', str(runner)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline and not result.exists():
                    time.sleep(.05)
                ready = json.loads(result.read_text())
                self.assertEqual(ready['pc_bind'], '127.0.0.1')
                base = f'http://127.0.0.1:{ready["pc_port"]}'
                with urllib.request.urlopen(base + '/' + ready['bundle_sha256'] + '.tar.gz', timeout=2) as response:
                    self.assertEqual(response.read(), bundle.read_bytes())
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(base + '/', timeout=2)
                self.assertEqual(error.exception.code, 404)
                process.send_signal(signal.SIGTERM)
                self.assertEqual(process.wait(timeout=5), 0)
                closed = json.loads(result.read_text())
                self.assertEqual(closed['successful_downloads'], 1)
                self.assertTrue(closed['s23_reverse_forward_process_closed'])
                with socket.socket() as probe:
                    self.assertNotEqual(probe.connect_ex(('127.0.0.1', ready['pc_port'])), 0)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=3)


if __name__ == '__main__':
    unittest.main()

"""Integration checks against disposable local Git remotes; no accounts/devices."""
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

import check_env

CONTROLLER = Path(__file__).with_name('work_session.py')


class WorkflowIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mestry-h2-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / 'checkout'
        self.remote = self.base / 'remote.git'
        self.storage = self.base / 'private'
        self.run_git(self.base, 'init', '--bare', '--initial-branch=main', str(self.remote))
        self.run_git(self.base, 'clone', str(self.remote), str(self.repo))
        self.run_git(self.repo, 'config', 'user.name', 'Fixture Developer')
        self.run_git(self.repo, 'config', 'user.email', 'fixture@example.invalid')
        self.write('calc.py', 'VALUE = 1\n')
        self.write('test_calc.py', 'import unittest\nfrom calc import VALUE\nclass Calc(unittest.TestCase):\n def test_value(self): self.assertGreater(VALUE, 0)\n')
        self.write('README.md', 'Synthetic project\n')
        self.write('NOTES.md', 'Local notes\n')
        self.write('dependency.txt', 'v1\n')
        self.write('.gitignore', '.env\n*.tmp\n__pycache__/\n')
        self.write('.gitattributes', (CONTROLLER.parent.parent / '.gitattributes').read_text())
        contract = {'schema': 1, 'project': 'fixture', 'remote': str(self.remote),
                    'branch': 'main', 'targets': [check_env.target()],
                    'requirements': {'python': '3.12'}, 'dependency_inputs': ['dependency.txt'],
                    'allowed_files': ['calc.py', 'test_calc.py', 'README.md', 'NOTES.md', 'dependency.txt', '.gitignore', '.gitattributes', '.mestry-workflow.json'],
                    'allowed_prefixes': ['docs/'], 'protected_files': ['.mestry-workflow.json'],
                    'validation': [{'name': 'fixture', 'argv': [sys.executable, '-B', '-m', 'unittest', 'discover', '-p', 'test_calc.py'], 'minimum_tests': 1}]}
        self.write('.mestry-workflow.json', json.dumps(contract))
        self.run_git(self.repo, 'add', '.')
        self.run_git(self.repo, 'commit', '-qm', 'Seed synthetic project')
        self.run_git(self.repo, 'push', '-qu', 'origin', 'main')
        self.command('configure', '--review-policy')
        self.state = self.storage / hashlib.sha256(os.fsencode(self.repo)).hexdigest()[:20]

    def run_git(self, cwd, *args):
        result = subprocess.run(['git', *args], cwd=cwd, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return result.stdout.decode().strip()

    def write(self, name, value, repo=None):
        path = (repo or self.repo) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def argv(self, *args):
        return [sys.executable, '-B', str(CONTROLLER), '--repo', str(self.repo), '--state-root', str(self.storage), *args]

    def command(self, *args, blocked=None):
        result = subprocess.run(self.argv(*args), capture_output=True, text=True, timeout=25)
        value = json.loads(result.stdout.splitlines()[-1])
        self.assertEqual(result.returncode, 3 if blocked else 0, value)
        if blocked:
            self.assertEqual(value['reason'], blocked)
        return value

    def head(self):
        return self.run_git(self.repo, 'rev-parse', 'HEAD')

    def index(self):
        return (self.repo / '.git/index').read_bytes()

    def peer_commit(self, name='calc.py', value='VALUE = 2\n'):
        peer = self.base / 'peer'
        if not peer.exists():
            self.run_git(self.base, 'clone', str(self.remote), str(peer))
            self.run_git(peer, 'config', 'user.name', 'Fixture Developer')
            self.run_git(peer, 'config', 'user.email', 'fixture@example.invalid')
        self.write(name, value, peer)
        self.run_git(peer, 'add', name)
        self.run_git(peer, 'commit', '-qm', 'Peer synthetic change')
        self.run_git(peer, 'push', '-q', 'origin', 'main')
        return self.run_git(peer, 'rev-parse', 'HEAD')

    def test_private_configuration(self):
        self.assertEqual((self.state / 'config.json').stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o700)
        self.assertFalse(self.state.is_relative_to(self.repo))
        self.assertFalse(self.command('check')['dirty'])

    def test_dirty_receive_preserves_files(self):
        self.write('calc.py', 'VALUE = 9\n')
        original = self.head(), self.index()
        self.command('receive', blocked='DIRTY_OR_UNTRACKED')
        self.assertEqual((self.head(), self.index()), original)
        self.assertEqual((self.repo / 'calc.py').read_text(), 'VALUE = 9\n')

    def test_untracked_receive_is_blocked(self):
        self.write('docs/new.md', 'Unpublished\n')
        self.command('receive', blocked='DIRTY_OR_UNTRACKED')
        self.assertTrue((self.repo / 'docs/new.md').exists())

    def test_staged_receive_is_blocked(self):
        self.write('README.md', 'Staged\n')
        self.run_git(self.repo, 'add', 'README.md')
        before = self.index()
        self.command('receive', blocked='DIRTY_OR_UNTRACKED')
        self.assertEqual(self.index(), before)

    def test_receive_validated_fast_forward(self):
        expected = self.peer_commit()
        result = self.command('receive')
        self.assertTrue(result['applied'])
        self.assertEqual(self.head(), expected)
        self.assertEqual(result['validation'][0]['tests'], 1)

    def test_bad_candidate_preserves_good_tree(self):
        before = self.head(), self.index(), (self.repo / 'calc.py').read_bytes()
        self.peer_commit(value='VALUE = -1\n')
        self.command('receive', blocked='VALIDATION_FAILED_FIXTURE')
        self.assertEqual((self.head(), self.index(), (self.repo / 'calc.py').read_bytes()), before)

    def test_changed_dependency_is_not_installed(self):
        self.peer_commit('dependency.txt', 'v2\n')
        before = self.head()
        self.command('receive', blocked='DEPENDENCIES_CHANGED_REVIEW_REQUIRED')
        self.assertEqual(self.head(), before)
        self.assertEqual((self.repo / 'dependency.txt').read_text(), 'v1\n')

    def test_preview_preserves_real_index(self):
        self.write('calc.py', 'VALUE = 5\n')
        before = self.head(), self.index()
        result = self.command('finish', 'calc.py')
        self.assertTrue(result['index_unchanged'])
        self.assertFalse(result['plan']['publication_requested'])
        self.assertEqual((self.head(), self.index()), before)

    def test_publish_only_selected_candidate(self):
        self.write('calc.py', 'VALUE = 5\n')
        self.write('NOTES.md', 'Still working\n')
        self.write('.env', 'Synthetic local setting\n')
        result = self.command('finish', '--publish', '--message', 'Reviewed fixture change', 'calc.py')
        self.assertTrue(result['remote_contains_commit'])
        self.assertTrue(result['remaining_local_changes'])
        self.assertEqual(self.run_git(self.repo, 'show', 'HEAD:NOTES.md'), 'Local notes')
        self.assertEqual(result['s23_received'], 'not_checked')

    def test_failed_validation_does_not_stage(self):
        self.write('calc.py', 'VALUE = -1\n')
        before = self.head(), self.index()
        self.command('finish', '--publish', 'calc.py', blocked='VALIDATION_FAILED_FIXTURE')
        self.assertEqual((self.head(), self.index()), before)

    def test_preexisting_unselected_index_preserved(self):
        self.write('NOTES.md', 'Staged note\n')
        self.run_git(self.repo, 'add', 'NOTES.md')
        before = self.index()
        self.command('finish', 'calc.py', blocked='PREEXISTING_INDEX_NOT_SELECTED')
        self.assertEqual(self.index(), before)

    def test_partial_staging_is_not_overwritten(self):
        self.write('calc.py', 'VALUE = 2\n')
        self.run_git(self.repo, 'add', 'calc.py')
        self.write('calc.py', 'VALUE = 3\n')
        before = self.index()
        self.command('finish', 'calc.py', blocked='PARTIAL_STAGING_REQUIRES_REVIEW')
        self.assertEqual(self.index(), before)

    def test_forced_secret_file_is_blocked(self):
        self.write('.env', 'Fixture configuration\n')
        self.run_git(self.repo, 'add', '-f', '.env')
        self.command('finish', '.env', blocked='PRIVATE_OR_GENERATED_PATH')

    def test_synthetic_secret_is_blocked(self):
        self.write('README.md', 'MESTRY_H1_SYNTHETIC_' + 'DO_NOT_PUBLISH')
        self.command('finish', 'README.md', blocked='SECRET_PATTERN')

    def test_secret_in_deleted_intermediate_commit_is_blocked(self):
        self.write('README.md', 'MESTRY_H1_SYNTHETIC_' + 'DO_NOT_PUBLISH')
        self.run_git(self.repo, 'add', 'README.md')
        self.run_git(self.repo, 'commit', '-qm', 'Synthetic history test')
        self.write('README.md', 'Synthetic project\n')
        self.run_git(self.repo, 'add', 'README.md')
        self.run_git(self.repo, 'commit', '-qm', 'Remove fixture marker')
        self.command('finish', '--publish', blocked='SECRET_PATTERN')

    def test_symlink_and_traversal_are_blocked(self):
        (self.repo / 'docs').symlink_to(self.base, target_is_directory=True)
        self.command('finish', 'docs/test.md', blocked='SYMLINK_PATH_NOT_ADMITTED')
        self.command('finish', '../escape.md', blocked='UNSAFE_PATH')

    def test_origin_mismatch(self):
        self.run_git(self.repo, 'remote', 'set-url', 'origin', str(self.base / 'other.git'))
        self.command('check', blocked='REMOTE_MISMATCH')

    def test_push_url_mismatch(self):
        self.run_git(self.repo, 'remote', 'set-url', '--push', 'origin', str(self.base / 'other.git'))
        self.command('check', blocked='REMOTE_MISMATCH')

    def test_branch_and_policy_require_review(self):
        self.run_git(self.repo, 'switch', '-c', 'fixture-branch')
        self.command('check', blocked='BRANCH_MISMATCH')
        self.run_git(self.repo, 'switch', 'main')
        with (self.repo / '.mestry-workflow.json').open('a') as out:
            out.write('\n')
        self.command('check', blocked='POLICY_REVIEW_REQUIRED')

    def test_divergence_preserves_both_histories(self):
        self.write('NOTES.md', 'Local branch work\n')
        self.run_git(self.repo, 'add', 'NOTES.md')
        self.run_git(self.repo, 'commit', '-qm', 'Local fixture change')
        before = self.head()
        remote = self.peer_commit()
        self.command('receive', blocked='DIVERGED')
        self.command('finish', '--publish', blocked='REMOTE_ADVANCED_OR_DIVERGED')
        self.assertEqual(self.head(), before)
        self.assertEqual(self.run_git(self.repo, 'rev-parse', 'origin/main'), remote)

    def test_offline_resume_preserves_unpublished_work(self):
        self.write('NOTES.md', 'Offline work\n')
        self.command('start', '--offline', '--', sys.executable, '-c', 'pass', blocked='DIRTY_WORKTREE_USE_RESUME')
        result = self.command('start', '--offline', '--resume', '--', sys.executable, '-c', 'pass')
        self.assertTrue(result['dirty'])

    def test_repeat_publication_does_not_create_commit(self):
        before = self.head()
        result = self.command('finish', '--publish')
        self.assertFalse(result['new_commit'])
        self.assertEqual(self.head(), before)

    def test_busy_until_detached_child_finishes(self):
        # The launcher exits immediately; its detached writer must still own the session.
        child = 'import time; from pathlib import Path; time.sleep(1.5); Path("NOTES.md").write_text("Background fixture done\\n")'
        launcher = 'import subprocess,sys; subprocess.Popen([sys.executable,"-c",' + repr(child) + '],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)'
        process = subprocess.Popen(self.argv('start', '--offline', '--', sys.executable, '-c', launcher), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertIn('SESSION_READY', process.stdout.readline())
            self.command('receive', blocked='BUSY')
            self.assertIsNone(process.poll())
            out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, (out, err))
            self.assertEqual((self.repo / 'NOTES.md').read_text(), 'Background fixture done\n')
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=10)

    def test_stale_running_session_requires_review(self):
        path = self.state / 'status.json'
        value = json.loads(path.read_text())
        value['phase'] = 'running'
        path.write_text(json.dumps(value))
        self.assertTrue(self.command('check')['recovery_required'])
        self.command('receive', blocked='UNCLEAN_SESSION_REVIEW_REQUIRED')

    def test_custom_hooks_require_review(self):
        hook = self.repo / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 0\n')
        hook.chmod(0o700)
        self.command('check', blocked='CUSTOM_HOOKS_REQUIRE_REVIEW')

    def test_network_failure_and_retry_preserve_work(self):
        self.command('receive')
        before = self.head(), self.index()
        success = json.loads((self.state / 'status.json').read_text())['last_success']
        missing = self.base / 'temporarily-offline.git'
        self.remote.rename(missing)
        self.command('receive', blocked='GIT_OPERATION_FAILED')
        self.assertEqual((self.head(), self.index()), before)
        self.assertEqual(json.loads((self.state / 'status.json').read_text())['last_success'], success)
        missing.rename(self.remote)
        self.command('receive')

    def test_signal_keeps_lock_until_detached_writer_finishes(self):
        child = 'import time; time.sleep(1.5)'
        launcher = 'import subprocess,sys; subprocess.Popen([sys.executable,"-c",' + repr(child) + '],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print("CHILD_READY",flush=True); import time; time.sleep(20)'
        process = subprocess.Popen(self.argv('start', '--offline', '--', sys.executable, '-c', launcher), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertIn('SESSION_READY', process.stdout.readline())
            self.assertIn('CHILD_READY', process.stdout.readline())
            process.send_signal(signal.SIGTERM)
            self.command('receive', blocked='BUSY')
            out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 3, (out, err))
            self.assertIn('COMMAND_FAILED_WORK_PRESERVED', out)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=10)

    def test_profiles_share_checkout_without_sharing_homes(self):
        homes = [self.base / 'account-a', self.base / 'account-b']
        for home in homes:
            home.mkdir()
            result = subprocess.run(self.argv('start', '--offline', '--', sys.executable, '-c', 'import os; from pathlib import Path; assert Path.cwd().name == "checkout"; assert os.environ["CODEX_HOME"].endswith(os.environ["EXPECTED_PROFILE"])'),
                                    env=dict(os.environ, CODEX_HOME=str(home), EXPECTED_PROFILE=home.name), capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout.decode())
        self.assertNotEqual(*homes)


    def test_public_fixture_preserves_crlf_in_clean_clone(self):
        name = 'docs/validation/h2-fixture/fixtures/literal.md'
        path = self.repo / name
        path.parent.mkdir(parents=True)
        original = b'title\r\nbody\r\n'
        path.write_bytes(original)
        self.command('finish', '--publish', name)
        clone = self.base / 'public-copy'
        self.run_git(self.base, 'clone', str(self.remote), str(clone))
        self.assertEqual((clone / name).read_bytes(), original)
        blob = self.run_git(clone, 'rev-parse', 'HEAD:' + name)
        self.assertEqual(self.run_git(clone, 'hash-object', '--path=' + name, name), blob)
        os.utime(clone / name, (1, 1))  # Force status to inspect bytes, not cached stat.
        self.assertEqual(self.run_git(clone, 'status', '--porcelain'), '')


if __name__ == '__main__':
    unittest.main()

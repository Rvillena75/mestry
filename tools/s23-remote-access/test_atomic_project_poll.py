import contextlib
from pathlib import Path
import unittest
from atomic_project_poll import fetch_only, updated_keeper_source, LEGACY_CALL, ATOMIC_CALL


class Blocked(Exception):
    pass


class SessionFixture:
    def __init__(self, phase='idle', busy=False):
        self.disk = {'phase': phase}
        self.state = {'phase': 'running'}  # Snapshot from the previous writer.
        self.busy, self.held, self.loaded, self.fetched = busy, False, False, False

    @contextlib.contextmanager
    def lock(self):
        if self.busy:
            raise Blocked('BUSY')
        self.held = True
        try:
            yield
        finally:
            self.held = False

    def load(self):
        if not self.held:
            raise AssertionError('snapshot read outside the lock')
        self.loaded = True
        self.state = dict(self.disk)

    def receive(self, *, fetch_only):
        assert self.held and fetch_only
        self.fetched = True
        return dict(head='old', remote='new', fetch_only=True, applied=False)

    def record(self, result, **fields):
        assert self.held
        self.disk.update(fields)


class AtomicPollTests(unittest.TestCase):
    def test_clean_release_replaces_the_old_running_snapshot(self):
        session = SessionFixture()
        code, result = fetch_only(session, Blocked)
        self.assertEqual(code, 0)
        self.assertTrue(result['fetch_only'])
        self.assertFalse(result['applied'])
        self.assertEqual(session.disk['phase'], 'idle')
        self.assertTrue(session.fetched)

    def test_busy_does_not_read_or_overwrite_an_active_writer(self):
        session = SessionFixture(phase='running', busy=True)
        before = dict(session.disk)
        code, result = fetch_only(session, Blocked)
        self.assertEqual((code, result['reason']), (3, 'BUSY'))
        self.assertFalse(session.loaded)
        self.assertEqual(session.disk, before)

    def test_real_recovery_is_preserved_without_fetch_or_reapproval(self):
        for phase in ('running', 'recovery_required'):
            session = SessionFixture(phase=phase)
            before = dict(session.disk)
            code, result = fetch_only(session, Blocked)
            self.assertEqual((code, result['reason']), (3, 'UNCLEAN_SESSION_REVIEW_REQUIRED'))
            self.assertFalse(session.fetched)
            self.assertEqual(session.disk, before)

    def test_existing_worker_patch_rejects_unknown_or_already_changed_code(self):
        source = Path(__file__).with_name('horus_keepalive.py').read_text()
        changed = updated_keeper_source(source)
        self.assertEqual(changed.replace(ATOMIC_CALL, LEGACY_CALL), source)
        self.assertEqual(changed.count(ATOMIC_CALL), 1)
        for other in ('unreviewed source', changed):
            with self.assertRaisesRegex(ValueError, 'EXISTING_POLL_CALL_REVIEW_REQUIRED'):
                updated_keeper_source(other)


if __name__ == '__main__':
    unittest.main()

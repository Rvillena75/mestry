#!/usr/bin/env python3
"""Fetch-only entry for the existing supervisor; load state after taking the lock."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

LEGACY_CALL = "[sys.executable, '-B', str(runner), '--repo', str(root),\n                                     'receive', '--fetch-only']"
ATOMIC_CALL = "[sys.executable, '-B', str(SELF.with_name('atomic_project_poll.py')),\n                                     '--repo', str(root)]"


def updated_keeper_source(source):
    """Prepare a reviewed code-only patch, without installing or starting anything."""
    if source.count(LEGACY_CALL) != 1 or ATOMIC_CALL in source:
        raise ValueError('EXISTING_POLL_CALL_REVIEW_REQUIRED')
    return source.replace(LEGACY_CALL, ATOMIC_CALL)


def fetch_only(session, blocked):
    # A state snapshot read before acquiring the lock may belong to the writer
    # that just released it. Never use that snapshot to declare recovery.
    try:
        with session.lock():
            session.load()
            if session.state.get('phase') in ('running', 'recovery_required'):
                raise blocked('UNCLEAN_SESSION_REVIEW_REQUIRED')
            result = session.receive(fetch_only=True)
            session.record('ok', phase='idle', last_success={
                'operation': 'atomic_fetch_only', 'head': result['head']})
        return 0, {'state': 'OK', 'action': 'receive', **result}
    except blocked as error:
        return 3, {'state': 'BLOCKED', 'reason': str(error), 'local_work_preserved': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    args = parser.parse_args()
    root = args.repo
    if not root.is_absolute() or root.is_symlink() or root.resolve() != root:
        raise ValueError('CANONICAL_PROJECT_REQUIRED')
    runner = root / 'tools/work_session.py'
    if not runner.is_file() or runner.is_symlink():
        raise ValueError('PROJECT_RUNNER_REQUIRED')
    sys.path.insert(0, str(runner.parent))
    spec = importlib.util.spec_from_file_location('mestry_reviewed_work_session', runner)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    code, result = fetch_only(module.Session(root), module.Blocked)
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError):
        print(json.dumps({'state': 'BLOCKED', 'reason': 'ATOMIC_POLL_FAILED_NO_PRIVATE_DETAILS',
                          'local_work_preserved': True}))
        raise SystemExit(3)

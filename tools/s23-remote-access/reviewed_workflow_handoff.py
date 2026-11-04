#!/usr/bin/env python3
"""Consume an explicitly reviewed, exact-SHA controller handoff at bridge lease entry.

No review is inferred or created here. Dependencies, contract, remote and identity
must be unchanged. Only controller/test pins can differ. The old checkout/policy
remain operative until the candidate has passed validation and fast-forwarded.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import types

ALLOWED_CHANGES = {'tools/work_session.py', 'tools/test_work_session.py'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()

def private_json(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('PRIVATE_REVIEW_REQUIRED')
    return json.loads(path.read_text())

def reviewed_policy(old, plan):
    if plan.get('schema') != 1 or plan.get('reviewed') is not True:
        raise ValueError('EXPLICIT_REVIEW_REQUIRED')
    if not all(re.fullmatch('[0-9a-f]{40}', plan.get(k, '')) for k in ('from_head', 'to_head')) or plan['from_head'] == plan['to_head']:
        raise ValueError('DISTINCT_REVIEWED_HEADS_REQUIRED')
    future = copy.deepcopy(plan['future_policy'])
    mutable = {'pins', 'controller_sha', 'approved_at', 'transition_review'}
    if {k:v for k,v in old.items() if k not in mutable} != {k:v for k,v in future.items() if k not in mutable}:
        raise ValueError('NON_CONTROL_POLICY_CHANGE_NOT_ADMITTED')
    if old['root'] != plan['root'] or set(old['pins']) != set(future['pins']):
        raise ValueError('POLICY_ROOT_OR_PIN_SET_CHANGED')
    changed = {k:{'before':old['pins'][k], 'after':future['pins'][k]}
               for k in old['pins'] if old['pins'][k] != future['pins'][k]}
    if not changed or not set(changed).issubset(ALLOWED_CHANGES) or changed != plan['protected_changes']:
        raise ValueError('PROTECTED_CHANGE_REVIEW_MISMATCH')
    if old['controller_sha'] != old['pins']['tools/work_session.py'] or future['controller_sha'] != future['pins']['tools/work_session.py']:
        raise ValueError('CONTROLLER_PIN_MISMATCH')
    if future.get('transition_review') != {'reviewed':True, 'from_head':plan['from_head'], 'to_head':plan['to_head']}:
        raise ValueError('EXACT_TRANSITION_REVIEW_REQUIRED')
    return future

def session_class(module, plan, config, plan_sha):
    Base = module.Session
    blocked = module.Blocked
    class HandoffSession(Base):
        def load(self):
            super().load()
            head = self.text('rev-parse', 'HEAD')
            if head == plan['from_head']:
                if sha(config.read_bytes()) != plan['policy_before_sha256']:
                    raise blocked('POLICY_CHANGED_AFTER_REVIEW')
                reviewed_policy(self.cfg, plan)
            elif head == plan['to_head']:
                if self.cfg != plan['future_policy']:
                    raise blocked('PROMOTED_POLICY_MISMATCH')
            else:
                raise blocked('HEAD_OUTSIDE_REVIEWED_HANDOFF')

        def fetch(self):
            ref = super().fetch()
            if self.text('rev-parse', ref) != plan['to_head']:
                raise blocked('REMOTE_OUTSIDE_REVIEWED_HANDOFF')
            return ref

        def validate(self, revision):
            if self.text('rev-parse', revision) != plan['to_head']:
                raise blocked('CANDIDATE_OUTSIDE_REVIEWED_HANDOFF')
            before = self.cfg
            self.cfg = reviewed_policy(before, plan)
            try:
                return super().validate(revision)
            finally:
                self.cfg = before

        def receive(self, fetch_only=False):
            if fetch_only:
                raise blocked('HANDOFF_REQUIRES_MANAGED_APPLY')
            result = super().receive(fetch_only=False)
            if self.text('rev-parse', 'HEAD') != plan['to_head'] or not result.get('applied'):
                raise blocked('REVIEWED_FAST_FORWARD_REQUIRED')
            future = reviewed_policy(self.cfg, plan)
            try:
                if sha(config.read_bytes()) != plan['policy_before_sha256']:
                    raise blocked('POLICY_CHANGED_AFTER_REVIEW')
                # This promotes the exact blob reviewed before entry. It does
                # not configure, infer approval or approve changed dependencies.
                module.write_private(config, future)
                self.cfg = future
                self.context()
                module.write_private(self.directory / ('handoff-' + plan['to_head'] + '.json'), {
                    'at':module.now(), 'head_before':plan['from_head'], 'head_after':plan['to_head'],
                    'plan_sha256':plan_sha, 'policy_before_sha256':plan['policy_before_sha256'],
                    'policy_after_sha256':sha(config.read_bytes()),
                    'validated_tree':self.state['validation']['tree'],
                    'protected_changes':plan['protected_changes'], 'approval_created':False})
            except BaseException:
                self.record('handoff_promotion_incomplete', phase='recovery_required')
                raise
            return result
    return HandoffSession

def git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, timeout=30,
                            env=dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0'))
    if result.returncode:
        raise ValueError('HANDOFF_GIT_QUERY_FAILED')
    return result.stdout

def run(plan_path, plan_sha, arguments):
    plan = private_json(plan_path)
    if sha(plan_path.read_bytes()) != plan_sha:
        raise ValueError('REVIEW_PLAN_DIGEST_MISMATCH')
    root = Path(plan['root'])
    if not root.is_absolute() or root.is_symlink() or root.resolve() != root:
        raise ValueError('CANONICAL_PROJECT_REQUIRED')
    runner = root / 'tools/work_session.py'
    args = list(arguments)
    if args[:1] == ['-B']:
        args.pop(0)
    if not args or Path(args.pop(0)).resolve() != runner or runner.is_symlink() or not runner.is_file():
        raise ValueError('MANAGED_LEASE_ENTRY_REQUIRED')
    globals_seen = {}
    pos = 0
    while pos < len(args) and args[pos] in ('--repo', '--state-root'):
        key = args[pos]
        if key in globals_seen or pos+1 >= len(args):
            raise ValueError('MANAGED_APPLY_ARGUMENTS_REQUIRED')
        globals_seen[key] = args[pos+1]
        pos += 2
    if globals_seen.get('--repo') is None or Path(globals_seen['--repo']).resolve() != root or args[pos:pos+1] != ['lease']:
        raise ValueError('MANAGED_LEASE_ENTRY_REQUIRED')
    tail = args[pos+1:]
    if tail and (len(tail) != 2 or tail[0] != '--writer-pid' or not tail[1].isdigit() or int(tail[1]) < 2):
        raise ValueError('MANAGED_APPLY_ARGUMENTS_REQUIRED')
    storage = Path(plan.get('state_root', str(Path.home()/'.local/state/mestry-workflow')))
    actual_storage = Path(globals_seen.get('--state-root', str(Path.home()/'.local/state/mestry-workflow')))
    if actual_storage.resolve() != storage.resolve():
        raise ValueError('STATE_ROOT_REVIEW_MISMATCH')
    config = storage / sha(os.fsencode(root))[:20] / 'config.json'
    old = private_json(config)
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    if head == plan['to_head']:
        if old != plan['future_policy'] or sha(runner.read_bytes()) != old['controller_sha']:
            raise ValueError('PROMOTED_POLICY_MISMATCH')
        os.execv(sys.executable, [sys.executable, '-B', str(runner), *args])
    if head != plan['from_head'] or sha(config.read_bytes()) != plan['policy_before_sha256']:
        raise ValueError('OPERATIVE_VERSION_CHANGED_AFTER_REVIEW')
    future = reviewed_policy(old, plan)
    checker = root / 'tools/check_env.py'
    if checker.is_symlink() or sha(checker.read_bytes()) != old['checker_sha']:
        raise ValueError('OPERATIVE_CHECKER_CHANGED')
    if sha(runner.read_bytes()) != old['controller_sha']:
        raise ValueError('OPERATIVE_CONTROLLER_CHANGED')
    source = git(root, 'show', plan['to_head'] + ':tools/work_session.py')
    if sha(source) != future['controller_sha']:
        raise ValueError('REVIEWED_CONTROLLER_DIGEST_MISMATCH')
    # Execute only the reviewed candidate controller, retaining the operative
    # file path for its old-policy checks until the managed fast-forward.
    sys.path.insert(0, str(runner.parent))
    module = types.ModuleType('mestry_reviewed_controller')
    module.__file__ = str(runner)
    sys.modules[module.__name__] = module
    exec(compile(source, str(runner), 'exec'), module.__dict__)
    module.Session = session_class(module, plan, config, plan_sha)
    sys.argv = [str(runner), *args]
    return module.main()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--plan-sha256', required=True)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
    try:
        return run(args.plan, args.plan_sha256, arguments)
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        reason = str(error) if isinstance(error, ValueError) and re.fullmatch('[A-Z_]+', str(error)) else 'HANDOFF_FAILED_NO_PRIVATE_DETAILS'
        print(json.dumps({'state':'BLOCKED', 'reason':reason, 'local_work_preserved':True}))
        return 3

if __name__ == '__main__':
    raise SystemExit(main())

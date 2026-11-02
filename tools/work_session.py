#!/usr/bin/env python3
"""Explicit project sessions using Git and a local cooperative lock; no daemon."""
import argparse
import contextlib
import ctypes
import fcntl
import fnmatch
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import time

import check_env

SOURCE = Path(__file__).resolve()
CONTRACT = ".mestry-workflow.json"
SENTINEL = "MESTRY_H1_SYNTHETIC_" + "DO_NOT_PUBLISH"


class Blocked(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def private_dir(path):
    if path.is_symlink():
        raise Blocked("UNSAFE_STATE_DIRECTORY")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.stat()
    if info.st_uid != os.getuid() or not stat.S_ISDIR(info.st_mode):
        raise Blocked("STATE_OWNER_MISMATCH")
    path.chmod(0o700)


def write_private(path, value):
    fd, temporary = tempfile.mkstemp(prefix=".state-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_private(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise Blocked("PRIVATE_STATE_PERMISSIONS")
    return json.loads(path.read_text())


class Session:
    def __init__(self, root, storage=None):
        self.root = root.resolve()
        base = storage or Path.home() / ".local/state/mestry-workflow"
        self.directory = base.resolve() / digest(os.fsencode(self.root))[:20]
        if self.directory.is_relative_to(self.root):
            raise Blocked("STATE_MUST_BE_OUTSIDE_CHECKOUT")
        self.cfg = None
        self.state = {}

    def git(self, *args, env=None, accept=(0,)):
        settings = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
        if env:
            settings.update(env)
        try:
            result = subprocess.run(["git", *args], cwd=self.root, env=settings,
                                    capture_output=True, timeout=45)
        except (OSError, subprocess.TimeoutExpired):
            raise Blocked("GIT_UNAVAILABLE_OR_TIMEOUT") from None
        if result.returncode not in accept:
            raise Blocked("GIT_OPERATION_FAILED")
        return result.stdout

    def text(self, *args, **kwargs):
        return self.git(*args, **kwargs).decode().strip()

    def configure(self):
        if Path(self.text("rev-parse", "--show-toplevel")).resolve() != self.root:
            raise Blocked("CHECKOUT_ROOT_MISMATCH")
        contract_path = self.root / CONTRACT
        if contract_path.is_symlink():
            raise Blocked("POLICY_SYMLINK")
        contract = json.loads(contract_path.read_text())
        if contract["schema"] != 1 or not contract["validation"]:
            raise Blocked("INVALID_CONTRACT")
        self.git("check-ref-format", "--branch", contract["branch"])
        self.cfg = {"schema": 1, "root": str(self.root), "contract": contract,
                    "controller_sha": digest(SOURCE.read_bytes()),
                    "checker_sha": digest(Path(check_env.__file__).read_bytes()),
                    "pins": {}, "approved_at": now(),
                    "author_email": self.text("config", "user.email")}
        for name in [CONTRACT, *contract.get("protected_files", [])]:
            if (self.root / name).is_symlink() or not (self.root / name).is_file():
                raise Blocked("POLICY_FILE_MISSING_OR_SYMLINK")
            self.cfg["pins"][name] = digest((self.root / name).read_bytes())
        self.context()
        environment = self.environment(approved=False)
        self.cfg["dependency_fingerprint"] = environment["dependency_fingerprint"]
        private_dir(self.directory)
        write_private(self.directory / "config.json", self.cfg)
        self.record("configured", environment=environment)
        return {"project": contract["project"], "target": environment["target"],
                "publication": "reviewed_explicit_paths_only", "auto_commit": False}

    def load(self):
        self.cfg = read_private(self.directory / "config.json")
        if self.cfg["root"] != str(self.root):
            raise Blocked("CONFIG_ROOT_MISMATCH")
        path = self.directory / "status.json"
        self.state = read_private(path) if path.exists() else {}
        self.context()

    @property
    def contract(self):
        return self.cfg["contract"]

    def context(self):
        if self.cfg["controller_sha"] != digest(SOURCE.read_bytes()) or self.cfg["checker_sha"] != digest(Path(check_env.__file__).read_bytes()):
            raise Blocked("CONTROLLER_REVIEW_REQUIRED")
        for name, expected in self.cfg["pins"].items():
            path = self.root / name
            if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != expected:
                raise Blocked("POLICY_REVIEW_REQUIRED")
        if Path(self.text("rev-parse", "--show-toplevel")).resolve() != self.root:
            raise Blocked("CHECKOUT_ROOT_MISMATCH")
        expected = self.contract["remote"]
        for extra in ((), ("--push",)):
            values = self.text("remote", "get-url", "--all", *extra, "origin").splitlines()
            if values != [expected]:
                raise Blocked("REMOTE_MISMATCH")
        if self.text("symbolic-ref", "--short", "HEAD") != self.contract["branch"]:
            raise Blocked("BRANCH_MISMATCH")
        for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
            path = Path(self.text("rev-parse", "--git-path", name))
            if (path if path.is_absolute() else self.root / path).exists():
                raise Blocked("GIT_OPERATION_IN_PROGRESS")
        if self.text("config", "--get", "core.hooksPath", accept=(0, 1)):
            raise Blocked("CUSTOM_HOOKS_REQUIRE_REVIEW")
        hooks = Path(self.text("rev-parse", "--git-path", "hooks"))
        hooks = hooks if hooks.is_absolute() else self.root / hooks
        if hooks.exists() and any(p.is_file() and not p.name.endswith('.sample') and os.access(p, os.X_OK) for p in hooks.iterdir()):
            raise Blocked("CUSTOM_HOOKS_REQUIRE_REVIEW")

    @contextlib.contextmanager
    def lock(self):
        private_dir(self.directory)
        path = self.directory / "session.lock"
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "a+") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Blocked("BUSY") from None
            yield handle

    def record(self, result, **fields):
        self.state.update({"schema": 1, "project": self.contract["project"],
                           "last_attempt": {"at": now(), "result": result}, **fields})
        write_private(self.directory / "status.json", self.state)

    def environment(self, root=None, approved=True):
        try:
            value = check_env.check(root or self.root, self.contract)
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
            raise Blocked("ENVIRONMENT_CHECK_FAILED") from None
        if value["errors"]:
            raise Blocked(value["errors"][0])
        if approved and value["dependency_fingerprint"] != self.cfg["dependency_fingerprint"]:
            raise Blocked("DEPENDENCIES_CHANGED_REVIEW_REQUIRED")
        return value

    def status(self):
        return self.text("status", "--porcelain=v1", "--untracked-files=all")

    def fetch(self):
        branch = self.contract["branch"]
        self.git("fetch", "--quiet", "--no-tags", "origin",
                 "refs/heads/" + branch + ":refs/remotes/origin/" + branch)
        self.state["remote_observed_at"] = now()
        return "refs/remotes/origin/" + branch

    def ancestor(self, left, right):
        result = subprocess.run(["git", "merge-base", "--is-ancestor", left, right],
                                cwd=self.root, capture_output=True, timeout=10)
        if result.returncode not in (0, 1):
            raise Blocked("ANCESTRY_UNKNOWN")
        return result.returncode == 0

    def permitted(self, name):
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or str(path) != name or any(ord(c) < 32 for c in name):
            raise Blocked("UNSAFE_PATH")
        if any(self.root.joinpath(*path.parts[:i]).is_symlink() for i in range(1, len(path.parts) + 1)):
            raise Blocked("SYMLINK_PATH_NOT_ADMITTED")
        if any(part in ('.git', '.ssh', 'node_modules', '.venv', 'venv', '__pycache__') or part.startswith('.codex') for part in path.parts):
            raise Blocked("PRIVATE_OR_GENERATED_PATH")
        forbidden = ('.env', '.env.*', 'auth.json', 'hosts.yml', 'credentials*.json',
                     'client_secret*.json', 'token*.json', '*.pem', '*.key', '*.p12',
                     '*.jks', '*.keystore', '*.sqlite*', '*.db', '*.apk', '*.aab', '*.pyc', '*.log', '*.tmp', 'id_ed25519*', 'id_rsa*')
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in forbidden):
            raise Blocked("PRIVATE_OR_GENERATED_PATH")
        if name.startswith('docs/validation/') and not name.endswith('.md'):
            raise Blocked("RAW_EVIDENCE_NOT_PUBLISHABLE")
        if name not in self.contract["allowed_files"] and not any(name.startswith(p) for p in self.contract["allowed_prefixes"]):
            raise Blocked("PATH_NOT_ADMITTED")

    def inspect_text(self, data):
        if b'\0' in data or len(data) > self.contract.get("max_file_bytes", 3000000):
            raise Blocked("BINARY_OR_OVERSIZE")
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            raise Blocked("TEXT_ENCODING_NOT_ADMITTED") from None
        if SENTINEL in text or re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
                r'\bgh[pousr]_[A-Za-z0-9]{25,}|\bgithub_pat_[A-Za-z0-9_]{30,}|'
                r'\bya29\.[A-Za-z0-9_-]{20,}|\b1//[A-Za-z0-9_-]{25,}|'
                r'\bGOCSPX-[A-Za-z0-9_-]{15,}|\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{30,}', text):
            raise Blocked("SECRET_PATTERN")
        if re.search(r'\bR5[A-Z0-9]{9}\b|\b[A-Za-z0-9._%+-]+@(?:gmail\.com|uc\.cl)\b|'
                     r'(?<![A-Za-z0-9_/])/home/(?!horus\b|harness_codex\b|developer\b|mestry\b)[A-Za-z0-9_-]+/', text):
            raise Blocked("PERSONAL_METADATA_REVIEW_REQUIRED")
        for match in re.finditer(r'''(?i)["'](?:access_token|refresh_token|client_secret|api_key|password)["']\s*[:=]\s*["']([^"'\r\n]{12,})["']''', text):
            value = match.group(1).lower()
            if not any(w in value for w in ('synthetic', 'fixture', 'fake', 'example', 'placeholder', 'redacted', 'sentinel')):
                raise Blocked("CREDENTIAL_LITERAL_REVIEW_REQUIRED")

    def inspect_tree(self, revision):
        entries = self.git("ls-tree", "-r", "-z", revision).split(b'\0')
        present = set()
        for row in filter(None, entries):
            metadata, raw_name = row.split(b'\t', 1)
            mode, kind, oid = metadata.split()
            name = raw_name.decode('utf-8')
            present.add(name)
            self.permitted(name)
            if kind != b'blob' or mode not in (b'100644', b'100755'):
                raise Blocked("SYMLINK_OR_SUBMODULE_NOT_ADMITTED")
            data = self.git("cat-file", "blob", oid.decode())
            self.inspect_text(data)
            if name in self.cfg["pins"] and digest(data) != self.cfg["pins"][name]:
                raise Blocked("CANDIDATE_POLICY_REVIEW_REQUIRED")
        if not set(self.cfg['pins']).issubset(present):
            raise Blocked('CANDIDATE_POLICY_FILE_MISSING')

    def validate(self, revision):
        self.inspect_tree(revision)
        archive = self.git("archive", "--format=tar", revision)
        with tempfile.TemporaryDirectory(prefix="candidate-", dir=self.directory) as temp:
            destination = Path(temp)
            with tarfile.open(fileobj=io.BytesIO(archive)) as source:
                members = source.getmembers()
                if len(members) > 5000 or sum(m.size for m in members) > 128000000:
                    raise Blocked("CANDIDATE_LIMIT")
                for member in members:
                    name = PurePosixPath(member.name)
                    if name.is_absolute() or '..' in name.parts or not (member.isfile() or member.isdir()):
                        raise Blocked("UNSAFE_ARCHIVE")
                    path = destination / str(name)
                    if member.isdir():
                        path.mkdir(parents=True, exist_ok=True)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        with source.extractfile(member) as body, path.open('xb') as out:
                            out.write(body.read())
                        path.chmod(0o700 if member.mode & 0o111 else 0o600)
            environment = self.environment(destination)
            results = []
            for rule in self.contract["validation"]:
                result = subprocess.run(rule["argv"], cwd=destination, capture_output=True, timeout=120)
                output = result.stdout + result.stderr
                match = re.search(rb'Ran (\d+) tests?|# tests (\d+)', output)
                count = int(next(v for v in match.groups() if v)) if match else 0
                if result.returncode or count < rule.get('minimum_tests', 0):
                    raise Blocked("VALIDATION_FAILED_" + rule['name'].upper())
                results.append({"name": rule["name"], "tests": count})
        self.state["validation"] = {"at": now(), "tree": self.text("rev-parse", revision + '^{tree}'),
                                    "environment": environment["dependency_fingerprint"], "results": results}
        return results

    def receive(self, fetch_only=False):
        self.environment()
        if not fetch_only and self.status():
            raise Blocked("DIRTY_OR_UNTRACKED")
        remote = self.fetch()
        head, incoming = self.text("rev-parse", "HEAD"), self.text("rev-parse", remote)
        if fetch_only:
            return {"head": head, "remote": incoming, "applied": False, "fetch_only": True}
        if head == incoming:
            return {"head": head, "applied": False}
        if not self.ancestor(head, remote):
            raise Blocked("LOCAL_AHEAD" if self.ancestor(remote, head) else "DIVERGED")
        results = self.validate(remote)
        self.context()
        if self.status() or self.text("rev-parse", "HEAD") != head:
            raise Blocked("CHECKOUT_CHANGED_DURING_VALIDATION")
        self.git("merge", "--ff-only", "--quiet", remote)
        return {"head": incoming, "applied": True, "validation": results}

    def outgoing(self, remote):
        for revision in self.text("rev-list", remote + '..HEAD').splitlines():
            for name in self.text("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", revision).splitlines():
                self.permitted(name)
            if self.text('show', '-s', '--format=%ae', revision) != self.cfg['author_email']:
                raise Blocked("AUTHOR_REVIEW_REQUIRED")
            self.inspect_text(self.git('show', '-s', '--format=%B', revision))
            self.inspect_tree(revision)

    def confirm(self, expected):
        rows = self.text("ls-remote", "--exit-code", "origin", 'refs/heads/' + self.contract['branch']).split()
        if not rows:
            raise Blocked("PUBLICATION_UNCONFIRMED")
        remote_head = rows[0]
        if remote_head != expected and not self.ancestor(expected, self.fetch()):
            raise Blocked("PUBLICATION_UNCONFIRMED")
        return {"published_head": expected, "remote_head": remote_head, "remote_contains_commit": True,
                "s23_received": "not_checked", "document_sync": "external_not_run"}

    def finish(self, paths, message, publish):
        self.environment()
        if len(paths) != len(set(paths)):
            raise Blocked("DUPLICATE_PATH")
        for name in paths:
            self.permitted(name)
        staged = set(self.text('diff', '--cached', '--name-only').splitlines())
        if not staged.issubset(paths):
            raise Blocked("PREEXISTING_INDEX_NOT_SELECTED")
        if staged.intersection(self.text('diff', '--name-only').splitlines()):
            raise Blocked("PARTIAL_STAGING_REQUIRES_REVIEW")
        self.inspect_text(message.encode())
        remote = self.fetch()
        self.outgoing(remote)
        if not self.ancestor(remote, 'HEAD'):
            raise Blocked("REMOTE_ADVANCED_OR_DIVERGED")
        head = self.text('rev-parse', 'HEAD')
        index_path = Path(self.text('rev-parse', '--git-path', 'index'))
        if not index_path.is_absolute():
            index_path = self.root / index_path
        original_index = index_path.read_bytes()
        selected = {p: digest((self.root / p).read_bytes()) if (self.root / p).is_file() and not (self.root / p).is_symlink() else None for p in paths}
        with tempfile.TemporaryDirectory(prefix='index-', dir=self.directory) as temp:
            index = Path(temp) / 'index'
            index.write_bytes(original_index)
            env = {'GIT_INDEX_FILE': str(index)}
            if paths:
                self.git('add', '--', *paths, env=env)
            tree = self.text('write-tree', env=env)
            self.inspect_tree(tree)
            changed = self.text('diff', '--cached', '--name-only', env=env).splitlines()
            plan = {"selected": sorted(paths), "candidate_tree": tree, "changed": changed,
                    "existing_outgoing_commits": len(self.text('rev-list', remote + '..HEAD').splitlines()),
                    "publication_requested": publish}
            if not publish:
                return {"plan": plan, "index_unchanged": index_path.read_bytes() == original_index}
            if self.text('config', 'user.email') != self.cfg['author_email']:
                raise Blocked('AUTHOR_REVIEW_REQUIRED')
            results = self.validate(tree)
            self.context()
            current = {p: digest((self.root / p).read_bytes()) if (self.root / p).is_file() and not (self.root / p).is_symlink() else None for p in paths}
            if selected != current or index_path.read_bytes() != original_index or self.text('rev-parse', 'HEAD') != head:
                raise Blocked('CHECKOUT_CHANGED_DURING_VALIDATION')
            remote = self.fetch()
            if not self.ancestor(remote, 'HEAD'):
                raise Blocked('REMOTE_ADVANCED_OR_DIVERGED')
            if changed:
                self.git('add', '--', *[p for p in paths if p not in staged])
                if self.text('write-tree') != tree:
                    raise Blocked('INDEX_CANDIDATE_CHANGED')
                self.git('commit', '--quiet', '-m', message)
                if self.text('rev-parse', 'HEAD^{tree}') != tree:
                    raise Blocked('COMMIT_CANDIDATE_CHANGED')
            self.outgoing(remote)
            expected = self.text('rev-parse', 'HEAD')
            # A lost acknowledgement is reconciled before declaring a pending push.
            try:
                self.git('push', '--quiet', 'origin', 'HEAD:refs/heads/' + self.contract['branch'])
            except Blocked:
                try:
                    confirmation = self.confirm(expected)
                except Blocked:
                    raise Blocked('PUBLICATION_PENDING_LOCAL_COMMIT_PRESERVED') from None
            else:
                confirmation = self.confirm(expected)
            return {**confirmation, "new_commit": bool(changed), "validation": results,
                    "remaining_local_changes": bool(self.status())}

    def check(self, probe=False):
        head = self.text('rev-parse', 'HEAD')
        remote_ref = 'refs/remotes/origin/' + self.contract['branch']
        counts = self.text('rev-list', '--left-right', '--count', 'HEAD...' + remote_ref, accept=(0, 128))
        relation = list(map(int, counts.split())) if re.fullmatch(r'\d+\s+\d+', counts) else [None, None]
        try:
            with self.lock():
                busy = False
        except Blocked:
            busy = True
        result = {"head": head, "branch": self.contract['branch'], "dirty": bool(self.status()),
                  "busy": busy, "ahead_cached": relation[0], "behind_cached": relation[1],
                  "phase": self.state.get('phase', 'idle'),
                  "recovery_required": self.state.get('phase') in ('running', 'recovery_required') and not busy,
                  "last_result": self.state.get('last_attempt'), "remote_observed_at": self.state.get('remote_observed_at'),
                  "s23_received": "not_checked", "document_sync": "external_not_run"}
        try:
            result['environment'] = self.environment()
        except Blocked as error:
            result['environment_error'] = str(error)
        if probe:
            try:
                result['remote_head'] = self.text('ls-remote', '--exit-code', 'origin', 'refs/heads/' + self.contract['branch']).split()[0]
                result['remote_matches_head'] = result['remote_head'] == head
            except (Blocked, IndexError):
                result['remote_error'] = 'UNAVAILABLE_LAST_SUCCESS_NOT_REPLACED'
        return result

    def start(self, command, resume=False, offline=False):
        if not command:
            raise Blocked('COMMAND_REQUIRED')
        self.environment()
        if offline:
            if self.status() and not resume:
                raise Blocked('DIRTY_WORKTREE_USE_RESUME')
            receive = {"offline": True, "remote_fresh": False}
        elif resume:
            self.fetch()
            receive = {"resumed_local_changes": True, "applied": False}
        else:
            receive = self.receive()
            if self.state.get('validation', {}).get('tree') != self.text('rev-parse', 'HEAD^{tree}'):
                self.validate('HEAD')
        self.record('running', phase='running')
        print(json.dumps({"state": "SESSION_READY", **receive}), flush=True)
        with run_foreground(command, self.root) as process:
            code = process.wait()
        if code:
            raise Blocked('COMMAND_FAILED_WORK_PRESERVED')
        return {"head": self.text('rev-parse', 'HEAD'), "dirty": bool(self.status()), "phase": "idle"}


@contextlib.contextmanager
def run_foreground(command, root):
    # Linux subreaper applies only to this foreground supervisor. Orphaned child
    # writers remain waitable even when they change their process group/session.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise Blocked('CHILD_LIFETIME_TRACKING_UNAVAILABLE')
    tty = sys.stdin.fileno() if sys.stdin.isatty() else None
    original = os.tcgetpgrp(tty) if tty is not None else None
    old_ttou = signal.signal(signal.SIGTTOU, signal.SIG_IGN)
    process = subprocess.Popen(command, cwd=root, process_group=0)
    def forward(signum, frame):
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            pass
    previous = {s: signal.signal(s, forward) for s in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)}
    if tty is not None:
        os.tcsetpgrp(tty, process.pid)
    try:
        yield process
    finally:
        # Do not release the checkout lock merely because the launcher exited.
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                break
            if pid == 0:
                time.sleep(.05)
        if tty is not None:
            os.tcsetpgrp(tty, original)
        for signum, handler in previous.items():
            signal.signal(signum, handler)
        signal.signal(signal.SIGTTOU, old_ttou)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=SOURCE.parent.parent)
    parser.add_argument('--state-root', type=Path)
    commands = parser.add_subparsers(dest='action', required=True)
    setup = commands.add_parser('configure')
    setup.add_argument('--review-policy', action='store_true', required=True)
    check = commands.add_parser('check')
    check.add_argument('--remote', action='store_true')
    receive = commands.add_parser('receive')
    receive.add_argument('--fetch-only', action='store_true')
    start = commands.add_parser('start')
    start.add_argument('--resume', action='store_true')
    start.add_argument('--offline', action='store_true')
    start.add_argument('command', nargs=argparse.REMAINDER)
    end = commands.add_parser('finish')
    end.add_argument('--publish', action='store_true')
    end.add_argument('--message', default='Reviewed MESTRY change')
    end.add_argument('paths', nargs='*')
    args = parser.parse_args()
    session = Session(args.repo, args.state_root)
    try:
        if args.action == 'configure':
            with session.lock():
                result = session.configure()
        else:
            session.load()
            if args.action == 'check':
                result = session.check(args.remote)
            else:
                with session.lock():
                    try:
                        if session.state.get('phase') in ('running', 'recovery_required'):
                            session.record('unclean_session', phase='recovery_required')
                            raise Blocked('UNCLEAN_SESSION_REVIEW_REQUIRED')
                        if args.action == 'receive':
                            result = session.receive(args.fetch_only)
                        elif args.action == 'finish':
                            result = session.finish(args.paths, args.message, args.publish)
                        else:
                            command = args.command[1:] if args.command[:1] == ['--'] else args.command
                            result = session.start(command, args.resume, args.offline)
                        session.record('ok', phase='idle', last_success={"at": now(), "operation": args.action, "head": session.text('rev-parse', 'HEAD')})
                    except (Blocked, OSError, ValueError, subprocess.TimeoutExpired):
                        session.record('blocked', phase='recovery_required' if session.state.get('phase') == 'recovery_required' else 'blocked')
                        raise
        print(json.dumps({"state": "OK", "action": args.action, **result}, sort_keys=True))
        return 0
    except (Blocked, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        reason = str(error) if isinstance(error, Blocked) else 'OPERATION_FAILED_NO_PRIVATE_DETAILS'
        print(json.dumps({"state": "BLOCKED", "reason": reason, "local_work_preserved": True}))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())

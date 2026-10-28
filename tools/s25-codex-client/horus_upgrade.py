#!/usr/bin/env python3
"""Replace only a verified bridge release, preserving pairing and session state."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile


def verify_release(source, digest=None):
    raw = (source / 'manifest.json').read_bytes()
    if digest is not None and hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('INSTALLED_MANIFEST_CHANGED')
    expected = json.loads(raw)['files']
    actual = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file() and p.relative_to(source) != Path('manifest.json')}
    if actual != set(expected) or any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('RELEASE_MEMBERS_CHANGED')
    for name, sha in expected.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or hashlib.sha256((source / relative).read_bytes()).hexdigest() != sha:
            raise ValueError('RELEASE_HASH_MISMATCH')
    return raw


def active_turns(state):
    count = 0
    for session in state.get('sessions', {}).values():
        active = set()
        for event in session.get('events', []):
            turn = event.get('turn_id')
            if event.get('event') == 'turn/started' and turn:
                active.add(turn)
            elif event.get('event') == 'turn/completed':
                active.discard(turn)
        count += len(active) + len(session.get('pending_approvals', {}))
    return count


def atomic_write(target, body, mode=0o600):
    fd, name = tempfile.mkstemp(prefix='.upgrade-', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, target)
    finally:
        Path(name).unlink(missing_ok=True)


def upgrade(source):
    home = Path.home()
    if str(home) != '/home/horus' or os.uname().machine != 'aarch64':
        raise ValueError('HORUS_SSH_PROFILE_REQUIRED')
    os.umask(0o077)
    base = home / '.local/lib/mestry-s25-pilot'
    pointer, controller = base / 'current.json', home / '.local/bin/mestry-bridge'
    state = home / '.local/state/mestry-s25-client'
    for path in (base, pointer, controller, state, state / 'bridge-token'):
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError('PRIVATE_INSTALL_PATH_REQUIRED')
    old_pointer, old_wrapper = pointer.read_bytes(), controller.read_bytes()
    old = json.loads(old_pointer)
    previous = Path(old['directory'])
    if previous.parent != base / 'releases':
        raise ValueError('INSTALLED_RELEASE_PATH_INVALID')
    verify_release(previous, old['manifest_sha256'])
    manifest = verify_release(source)
    release = base / 'releases' / hashlib.sha256(manifest).hexdigest()[:20]
    if release.exists():
        raise ValueError('RELEASE_ALREADY_EXISTS_INSPECT_FIRST')
    # Never restart the server in the middle of a user's task.
    if active_turns(json.loads((state / 'state.json').read_bytes())):
        raise ValueError('ACTIVE_TURN_OR_APPROVAL_FINISH_BEFORE_UPGRADE')
    token_before = (state / 'bridge-token').stat()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = base / 'backups' / (stamp + '-' + previous.name)
    backup.mkdir(parents=True, mode=0o700)
    atomic_write(backup / 'current.json', old_pointer)
    atomic_write(backup / 'mestry-bridge', old_wrapper, 0o700)
    shutil.copytree(source, release)
    for path in release.rglob('*'):
        os.chmod(path, 0o700 if path.is_dir() else 0o600)
    stopped = subprocess.run([str(controller), 'stop'], capture_output=True, timeout=15)
    if stopped.returncode:
        raise ValueError('OLD_BRIDGE_STOP_FAILED_NO_POINTER_CHANGE')
    new_pointer = json.dumps({'directory': str(release), 'manifest_sha256': hashlib.sha256(manifest).hexdigest()}).encode()
    new_wrapper = ('#!/bin/sh\nexec /usr/bin/python3 "' + str(release / 'horus_control.py') + '" "$@"\n').encode()
    try:
        atomic_write(pointer, new_pointer)
        atomic_write(controller, new_wrapper, 0o700)
        started = subprocess.run([str(controller), 'start'], capture_output=True, timeout=30)
        if started.returncode:
            raise ValueError('NEW_BRIDGE_START_FAILED')
    except Exception:
        subprocess.run([str(controller), 'stop'], capture_output=True, timeout=15)
        atomic_write(pointer, old_pointer)
        atomic_write(controller, old_wrapper, 0o700)
        restored = subprocess.run([str(controller), 'start'], capture_output=True, timeout=30)
        raise ValueError('UPGRADE_FAILED_ROLLED_BACK' if restored.returncode == 0 else 'ROLLBACK_START_FAILED') from None
    token_after = (state / 'bridge-token').stat()
    if (token_before.st_ino, token_before.st_mtime_ns, token_before.st_size) != (token_after.st_ino, token_after.st_mtime_ns, token_after.st_size):
        raise ValueError('PAIRING_METADATA_CHANGED_INSPECT_PRIVATELY')
    print(json.dumps({'status': 'PASS', 'marker': 'MESTRY_BRIDGE_UPGRADED',
                      'release': release.name, 'previous_release_retained': True,
                      'pairing_preserved': True, 'session_state_preserved': True,
                      'ports_unchanged': True, 'approval_policy': 'never',
                      'drive_oauth_in_horus': False}))


if __name__ == '__main__':
    try:
        upgrade(Path(__file__).resolve().parent)
    except Exception as error:
        code = str(error) if type(error) is ValueError else 'UPGRADE_FAILED_NO_RAW_OUTPUT'
        print(json.dumps({'status': 'ERROR', 'code': code}))
        raise SystemExit(1)

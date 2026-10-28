#!/usr/bin/env python3
"""Private Horus pilot controller. Never prints pairing credentials or raw logs."""
import argparse
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import warnings

HOME = Path.home()
STATE = HOME / '.local/state/mestry-s25-client'
RELEASE = HOME / '.local/lib/mestry-s25-pilot/current.json'
PID = STATE / 'process.json'
TOKEN = STATE / 'bridge-token'


def write_private(path, data):
    temporary = path.with_name(path.name + '.new')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def identity(pid):
    """PID plus Linux start-time, not PID alone; never signal an unrelated process."""
    status = Path(f'/proc/{pid}/stat').read_text()
    fields = status[status.rfind(')') + 2:].split()
    command = Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
    return fields[19], command


def owned_process(entry):
    try:
        record = json.loads(PID.read_text())
        pid = record['pid']
        if type(pid) is not int or pid < 2:
            return None
        start, command = identity(pid)
        if (start != record['start_time'] or
                str(entry).encode() not in command or os.getpgid(pid) != pid):
            return None
        return pid
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return None


def healthy():
    try:
        with urllib.request.urlopen('http://127.0.0.1:8787/healthz', timeout=.5) as response:
            result = json.loads(response.read(4096))
        return result.get('name') == 'mestry-s25-pilot' and result.get('version') == '0.1.0'
    except Exception:
        return False


def occupied():
    try:
        with socket.create_connection(('127.0.0.1', 8787), timeout=.3):
            return True
    except OSError:
        return False


def execute(action, rotate=False):
    if str(HOME) != '/home/horus' or os.uname().machine != 'aarch64':
        raise ValueError('HORUS_SSH_PROFILE_REQUIRED')
    os.umask(0o077)
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    if STATE.is_symlink() or STATE.stat().st_mode & 0o077:
        raise ValueError('PRIVATE_STATE_REQUIRED')
    release_record = json.loads(RELEASE.read_text())
    release = Path(release_record['directory'])
    if release.parent != HOME / '.local/lib/mestry-s25-pilot/releases':
        raise ValueError('RELEASE_PATH_INVALID')
    entry = release / 'src/mestry-entry.mjs'
    if not entry.is_file():
        raise ValueError('INSTALLED_ENTRY_REQUIRED')
    manifest_bytes = (release / 'manifest.json').read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != release_record['manifest_sha256']:
        raise ValueError('RELEASE_MANIFEST_CHANGED')
    for name, digest in json.loads(manifest_bytes)['files'].items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('RELEASE_MEMBER_INVALID')
        member = release / relative
        if member.is_symlink() or hashlib.sha256(member.read_bytes()).hexdigest() != digest:
            raise ValueError('RELEASE_FILE_CHANGED')
    pid = owned_process(entry)
    if action == 'pair':
        if pid or occupied():
            raise ValueError('STOP_BRIDGE_AND_BOOTSTRAP_TUNNEL_BEFORE_PAIRING')
        if TOKEN.exists() and not rotate:
            raise ValueError('PAIRING_EXISTS_USE_EXPLICIT_ROTATE_ONLY_IF_NEEDED')
        if not sys.stdin.isatty():
            raise ValueError('PRIVATE_INTERACTIVE_TERMINAL_REQUIRED')
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            value = getpass.getpass('Pega la clave generada en MESTRY Piloto (ingreso oculto): ').strip()
        if not re.fullmatch(r'[A-Za-z0-9_-]{43,128}', value):
            raise ValueError('GENERATED_PAIRING_KEY_REQUIRED')
        write_private(TOKEN, value + '\n')
        del value
        print('MESTRY_PRIVATE_PAIRING_SAVED')
        return
    if action == 'status':
        print(json.dumps({'marker': 'MESTRY_BRIDGE_STATUS', 'owned_process_running': bool(pid),
                          'loopback_health_matches': healthy() if pid else False,
                          'pairing_present': TOKEN.is_file(), 'port': 8787}))
        return
    if action == 'stop':
        if not pid:
            print('MESTRY_NO_OWNED_BRIDGE_RUNNING')
            return
        os.killpg(pid, signal.SIGTERM)
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline and owned_process(entry):
            time.sleep(.1)
        if owned_process(entry) == pid:
            os.killpg(pid, signal.SIGKILL)
        PID.unlink(missing_ok=True)
        print('MESTRY_OWNED_BRIDGE_STOPPED')
        return
    if pid:
        if not healthy():
            raise ValueError('OWNED_BRIDGE_NOT_READY_NO_DUPLICATE_STARTED')
        print('MESTRY_BRIDGE_ALREADY_RUNNING')
        return
    if occupied():
        raise ValueError('PORT_8787_OCCUPIED_NO_CHANGE')
    if not TOKEN.is_file() or TOKEN.is_symlink() or TOKEN.stat().st_mode & 0o077:
        raise ValueError('PRIVATE_PAIRING_REQUIRED')
    node = Path('/usr/bin/node')
    if not node.is_file():
        raise ValueError('EXISTING_NODE_REQUIRED_NO_INSTALL_ATTEMPTED')
    with (STATE / 'bridge.log').open('ab') as output:
        os.chmod(STATE / 'bridge.log', 0o600)
        process = subprocess.Popen([str(node), str(entry)], cwd='/workspace/projects/mestry-horus-smoke',
                                   stdin=subprocess.DEVNULL, stdout=output, stderr=output, start_new_session=True)
    start, _ = identity(process.pid)
    write_private(PID, json.dumps({'pid': process.pid, 'start_time': start}))
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise ValueError('BRIDGE_START_FAILED_NO_RAW_LOG_OUTPUT')
        if healthy():
            print('MESTRY_HORUS_BRIDGE_READY 127.0.0.1:8787')
            return
        time.sleep(.2)
    if owned_process(entry) == process.pid:
        os.killpg(process.pid, signal.SIGTERM)
    raise ValueError('BRIDGE_START_TIMEOUT_STOP_REQUESTED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['pair', 'start', 'status', 'stop'])
    parser.add_argument('--rotate', action='store_true')
    args = parser.parse_args()
    try:
        execute(args.action, args.rotate)
    except (KeyboardInterrupt, EOFError):
        print('MESTRY_BRIDGE_ACTION_INTERRUPTED_NO_SECRET_OUTPUT', file=sys.stderr)
        raise SystemExit(1)
    except Exception as error:
        # Only locally defined constant error codes are printable.
        code = str(error) if type(error) is ValueError and re.fullmatch('[A-Z0-9_]+', str(error)) else 'ACTION_FAILED_NO_RAW_OUTPUT'
        print('MESTRY_BRIDGE_' + code, file=sys.stderr)
        raise SystemExit(1)

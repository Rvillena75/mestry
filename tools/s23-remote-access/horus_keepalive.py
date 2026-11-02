#!/usr/bin/env python3
"""Supervise only the existing bridge in Horus. No credentials, model calls or new ports."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time
import urllib.request

STATE = Path.home() / '.local/state/mestry-keepalive'
CONTROLLER = Path.home() / '.local/bin/mestry-bridge'
SELF = Path(__file__).resolve()
PID = STATE / 'process.json'
STATUS = STATE / 'status.json'
ENABLED = STATE / 'enabled'


def private_write(path, value):
    temporary = path.with_name(path.name + '.new')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(json.dumps(value) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def identity(pid):
    fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
    return fields[19], Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')


def owned_worker():
    try:
        record = json.loads(PID.read_text())
        pid = record['pid']
        if type(pid) is not int or pid < 2:
            return None
        start, command = identity(pid)
        if start != record['start_time'] or str(SELF).encode() not in command or b'--worker' not in command:
            return None
        if os.getpgid(pid) != pid:
            return None
        return pid
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return None


def healthy():
    try:
        with urllib.request.urlopen('http://127.0.0.1:8787/healthz', timeout=2) as response:
            data = json.loads(response.read(4096))
        return data.get('name') == 'mestry-s25-pilot' and data.get('version') == '0.1.0'
    except Exception:
        return False


def controller(action):
    # The existing controller verifies its installed release and PID ownership.
    result = subprocess.run([str(CONTROLLER), action], capture_output=True, text=True, timeout=25)
    if action == 'status':
        if result.returncode != 0:
            raise ValueError('CONTROLLER_STATUS_FAILED')
        data = json.loads(result.stdout)
        if data.get('marker') != 'MESTRY_BRIDGE_STATUS' or type(data.get('owned_process_running')) is not bool:
            raise ValueError('CONTROLLER_STATUS_INVALID')
        return data['owned_process_running']
    return result.returncode == 0


def recover(check_health, run_controller):
    if check_health():
        return 'healthy'
    # A live but unresponsive bridge might own a task. Never kill it automatically.
    if run_controller('status'):
        return 'degraded_owned_process'
    if not run_controller('start'):
        return 'restart_failed'
    return 'recovered' if check_health() else 'starting'


def poll_projects():
    """Optional existing-worker task: fetch references only, never apply files."""
    config = STATE / 'projects.json'
    if not config.exists():
        return None
    try:
        info = config.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError('PRIVATE_PROJECT_CONFIG_REQUIRED')
        value = json.loads(config.read_text())
        roots = value['projects']
        if value['schema'] != 1 or not isinstance(roots, list) or not 1 <= len(roots) <= 4:
            raise ValueError('PROJECT_CONFIG_INVALID')
        results = []
        for item in roots:
            root = Path(item)
            if not root.is_absolute() or root.is_symlink() or root.resolve() != root:
                raise ValueError('PROJECT_ROOT_INVALID')
            runner = root / 'tools/work_session.py'
            if not runner.is_file() or runner.is_symlink():
                raise ValueError('PROJECT_RUNNER_REQUIRED')
            result = subprocess.run([sys.executable, '-B', str(runner), '--repo', str(root),
                                     'receive', '--fetch-only'], capture_output=True, text=True, timeout=50)
            response = json.loads(result.stdout.splitlines()[-1])
            if result.returncode == 0 and response.get('state') == 'OK' and response.get('fetch_only'):
                results.append({'project': root.name, 'state': 'fetched', 'head': response['head'],
                                'remote': response['remote'], 'update_pending': response['head'] != response['remote']})
            else:
                reason = response.get('reason', '')
                reason = reason if isinstance(reason, str) and re.fullmatch('[A-Z_0-9]+', reason) else 'FETCH_FAILED'
                results.append({'project': root.name, 'state': 'deferred' if reason == 'BUSY' else 'blocked', 'reason': reason})
        return {'state': 'checked', 'projects': results}
    except Exception:
        return {'state': 'project_poll_failed_no_private_details'}


def worker():
    with (STATE / 'worker.lock').open('a') as lock:
        os.chmod(STATE / 'worker.lock', 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        start, _ = identity(os.getpid())
        private_write(PID, {'pid': os.getpid(), 'start_time': start})
        def stop_signal(signum, frame):
            raise SystemExit(0)
        signal.signal(signal.SIGTERM, stop_signal)
        signal.signal(signal.SIGINT, stop_signal)
        attempts = 0
        next_project_poll = 0
        project_status = None
        try:
            while ENABLED.is_file():
                try:
                    state = recover(healthy, controller)
                except Exception:
                    state = 'check_failed_no_raw_output'
                attempts = 0 if state in {'healthy', 'recovered'} else attempts + 1
                if time.monotonic() >= next_project_poll:
                    project_status = poll_projects()
                    next_project_poll = time.monotonic() + 120
                private_write(STATUS, {'state': state, 'checked_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                                       'consecutive_failures': attempts, 'project_poll': project_status})
                time.sleep(30 if attempts < 5 else 300)
        finally:
            if owned_worker() == os.getpid():
                PID.unlink(missing_ok=True)


def execute(action):
    if str(Path.home()) != '/home/horus' or os.uname().machine != 'aarch64':
        raise ValueError('HORUS_PROFILE_REQUIRED')
    if not CONTROLLER.is_file() or CONTROLLER.is_symlink():
        raise ValueError('EXISTING_BRIDGE_CONTROLLER_REQUIRED')
    os.umask(0o077)
    STATE.mkdir(parents=True, mode=0o700, exist_ok=True)
    if STATE.is_symlink() or STATE.stat().st_mode & 0o077:
        raise ValueError('PRIVATE_STATE_REQUIRED')
    if action == '--worker':
        worker()
        return
    pid = owned_worker()
    if action == 'status':
        print(json.dumps({'marker': 'MESTRY_HORUS_KEEPALIVE', 'worker_running': bool(pid),
                          'enabled': ENABLED.is_file(), 'loopback_health_matches': healthy(),
                          'new_ports': False, 'reboot_recovery_verified': False}))
    elif action == 'stop':
        ENABLED.unlink(missing_ok=True)
        if pid:
            os.kill(pid, signal.SIGTERM)
        print('MESTRY_KEEPALIVE_STOP_REQUESTED_BRIDGE_UNCHANGED')
    else:
        if not ENABLED.exists():
            with ENABLED.open('x') as stream:
                stream.write('enabled\n')
            ENABLED.chmod(0o600)
        if not pid:
            subprocess.Popen([sys.executable, str(SELF), '--worker'], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        deadline = time.monotonic() + 4
        while not owned_worker() and time.monotonic() < deadline:
            time.sleep(.1)
        if not owned_worker():
            raise ValueError('WORKER_START_FAILED')
        print('MESTRY_KEEPALIVE_RUNNING_NO_NEW_PORTS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', choices=['start', 'status', 'stop'], default='status')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        execute('--worker' if args.worker else args.action)
    except Exception as error:
        code = str(error) if type(error) is ValueError and re.fullmatch('[A-Z0-9_]+', str(error)) else 'ACTION_FAILED_NO_RAW_OUTPUT'
        print('MESTRY_KEEPALIVE_' + code, file=sys.stderr)
        raise SystemExit(1)

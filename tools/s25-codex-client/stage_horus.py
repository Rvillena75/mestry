#!/usr/bin/env python3
"""Stage code over a bounded, private SSH reverse forward; never sends a secret."""
import argparse
import hashlib
import http.server
import json
from pathlib import Path
import shlex
import signal
import subprocess
import threading
import time

SSH = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'ControlMaster=no',
       '-o', 'ControlPath=none', '-o', 'StrictHostKeyChecking=yes', '-o', 'IdentityAgent=none',
       '-o', 'IdentitiesOnly=yes', '-o', 'ExitOnForwardFailure=yes',
       '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=2']


def policy_command():
    code = '''import json,os,subprocess
values = dict((parts[0].lower(), parts[1]) for line in subprocess.check_output(
    ["sshd", "-T"], stderr=subprocess.DEVNULL, text=True).splitlines()
    if len(parts := line.split(None, 1)) == 2)
print(json.dumps({"uid": os.getuid(), "port": values.get("port"),
    "gatewayports": values.get("gatewayports"), "allowtcpforwarding": values.get("allowtcpforwarding")}))
'''
    return 'python3 -I -c ' + shlex.quote(code)


def stage(bundle, output, seconds):
    if seconds < 30 or seconds > 600:
        raise ValueError('Use a bounded transfer window, 30 to 600 seconds')
    body = bundle.read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    route = '/' + digest + '.tar.gz'
    downloads = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != route:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/gzip')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            try:
                self.wfile.write(body)
                downloads.append(time.time())
            except OSError:
                pass

        def log_message(self, *_args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    ssh = None
    stopped = threading.Event()
    signal.signal(signal.SIGINT, lambda *_args: stopped.set())
    signal.signal(signal.SIGTERM, lambda *_args: stopped.set())
    try:
        check = subprocess.run(SSH + ['mestry-s23', policy_command()],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=15)
        policy = json.loads(check.stdout) if check.returncode == 0 else {}
        if policy != {'uid': 10348, 'port': '8023', 'gatewayports': 'no', 'allowtcpforwarding': 'yes'}:
            raise ValueError('EXPECTED_TERMUX_LOOPBACK_FORWARDING_POLICY_REQUIRED')
        # The already paired Termux key is used only for this tunnel, not Horus login.
        ssh = subprocess.Popen(SSH + ['-N', '-R', f'127.0.0.1:8787:127.0.0.1:{server.server_port}', 'mestry-s23'],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        if ssh.poll() is not None:
            raise ValueError('SSH_FORWARD_FAILED_NO_CHANGE_TO_OCCUPIED_PORT')
        status = {'status': 'TEMPORARY_CODE_TRANSFER_READY', 'pid': __import__('os').getpid(),
                  'pc_bind': '127.0.0.1', 'pc_port': server.server_port,
                  's23_bind': '127.0.0.1:8787', 'bundle_sha256': digest, 'max_seconds': seconds,
                  'no_credentials_served': True}
        output.write_text(json.dumps(status, indent=2) + '\n')
        output.chmod(0o600)
        print(json.dumps(status), flush=True)
        stopped.wait(seconds)
    finally:
        if ssh and ssh.poll() is None:
            ssh.terminate()
            try:
                ssh.wait(timeout=5)
            except subprocess.TimeoutExpired:
                ssh.kill()
                ssh.wait(timeout=2)
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        final = {'status': 'TEMPORARY_CODE_TRANSFER_CLOSED', 'successful_downloads': len(downloads),
                 's23_reverse_forward_process_closed': ssh is None or ssh.poll() is not None}
        output.write_text(json.dumps(final, indent=2) + '\n')
        print(json.dumps(final), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('result', type=Path)
    parser.add_argument('--seconds', type=int, default=600)
    args = parser.parse_args()
    stage(args.bundle, args.result, args.seconds)

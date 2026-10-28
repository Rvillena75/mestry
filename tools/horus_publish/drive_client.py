#!/usr/bin/env python3
"""Horus bridge capability client. No OAuth data or arbitrary SSH commands."""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


def main():
    home = Path.home()
    if str(home) != "/home/horus":
        raise ValueError("HORUS_PROFILE_REQUIRED")
    raw = sys.stdin.buffer.read(10001)
    if len(raw) > 10000:
        raise ValueError("DRIVE_REQUEST_TOO_LARGE")
    # Native Termux validates the exact operation/fields and the enabled folders.
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("DRIVE_REQUEST_INVALID")
    key = home / ".ssh/id_ed25519_mestry_publish"
    known = home / ".ssh/mestry_publish_known_hosts"
    for path in (key, known):
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("SSH_PRIVATE_PATH_UNSAFE")
    args = ["ssh", "-F", "/dev/null", "-T", "-p", "8023", "-i", str(key),
            "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes", "-o", "IdentityAgent=none",
            "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=" + str(known),
            "-o", "GlobalKnownHostsFile=/dev/null", "-o", "ControlMaster=no",
            "-o", "ControlPath=none", "-o", "ConnectTimeout=10", "-o", "ClearAllForwardings=yes",
            "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=2",
            "u0_a348@127.0.0.1", "mestry-drive-v1"]
    try:
        proc = subprocess.run(args, input=raw, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=140)
    except subprocess.TimeoutExpired:
        raise ValueError("DRIVE_REQUEST_TIMEOUT") from None
    if len(proc.stdout) > 1000000:
        raise ValueError("DRIVE_RESPONSE_TOO_LARGE")
    value = json.loads(proc.stdout)
    if not isinstance(value, dict):
        raise ValueError("DRIVE_RESPONSE_INVALID")
    if proc.returncode and value.get("status") != "ERROR":
        raise ValueError("DRIVE_SSH_FAILED")
    print(json.dumps(value, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        code = str(error) if type(error) is ValueError and str(error).replace("_", "").isupper() else "DRIVE_CAPABILITY_FAILED"
        print(json.dumps({"status": "ERROR", "code": code}))
        sys.exit(1)

#!/usr/bin/env python3
"""Horus-side publisher. No Google credentials; fixed local SSH capability."""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

ROOT = Path("/workspace/projects/mestry-horus-smoke")
DOCUMENT = "S23_PUBLISH_TEST.md"
KEY = Path.home() / ".ssh/id_ed25519_mestry_publish"
KNOWN_HOSTS = Path.home() / ".ssh/mestry_publish_known_hosts"


def read_document(root, name):
    if name != DOCUMENT or root.is_symlink() or root.resolve() != root:
        raise ValueError("DOCUMENT_NOT_ALLOWED")
    fd = os.open(root / name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise ValueError("REGULAR_FILE_REQUIRED")
        content = f.read(65537)
    if not content or len(content) > 65536:
        raise ValueError("CONTENT_SIZE")
    text = content.decode("utf-8")
    if any(ord(c) < 32 and c not in "\r\n\t" for c in text) or "\x7f" in text:
        raise ValueError("CONTENT_CONTROL_CHARACTER")
    return content


def make_request(content):
    digest = hashlib.sha256(content).hexdigest()
    request_id = hashlib.sha256((DOCUMENT + "\0" + digest).encode("ascii")).hexdigest()
    return {"schema": 1, "document": DOCUMENT, "sha256": digest, "request_id": request_id,
            "content_base64": base64.b64encode(content).decode("ascii")}


def ssh_args(command):
    return ["ssh", "-F", "/dev/null", "-T", "-p", "8023", "-i", str(KEY),
            "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes", "-o", "IdentityAgent=none",
            "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=" + str(KNOWN_HOSTS),
            "-o", "GlobalKnownHostsFile=/dev/null", "-o", "ControlMaster=no",
            "-o", "ControlPath=none", "-o", "ConnectTimeout=10", "-o", "ClearAllForwardings=yes",
            "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=2",
            "u0_a348@127.0.0.1", command]


def main():
    if len(sys.argv) != 2:
        raise ValueError("USE: mestry-publish S23_PUBLISH_TEST.md")
    content = read_document(ROOT, sys.argv[1])
    request = make_request(content)
    for p in (KEY, KNOWN_HOSTS):
        info = p.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) & 0o077):
            raise ValueError("SSH_PRIVATE_PATH_UNSAFE")
    try:
        # No shell; destination and SSH command are constants, not model input.
        proc = subprocess.run(ssh_args("mestry-publish-v1"), input=json.dumps(request).encode(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=150)
    except subprocess.TimeoutExpired:
        raise ValueError("RESULT_UNKNOWN_RETRY_IDENTICAL_FILE") from None
    if len(proc.stdout) > 10000:
        raise ValueError("RESPONSE_TOO_LARGE")
    try:
        result = json.loads(proc.stdout)
    except (ValueError, UnicodeError):
        raise ValueError("SSH_FAILED_OR_RESULT_UNKNOWN_RETRY_IDENTICAL_FILE") from None
    if proc.returncode or result.get("status") != "PUBLISHED_VERIFIED":
        code = result.get("code", "RESULT_UNKNOWN_RETRY_IDENTICAL_FILE")
        if not isinstance(code, str) or not all(c.isupper() or c.isdigit() or c == "_" for c in code):
            code = "INVALID_ERROR_RESPONSE"
        raise ValueError(code)
    if result.get("sha256") != request["sha256"] or result.get("request_id") != request["request_id"]:
        raise ValueError("RESPONSE_HASH_MISMATCH")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as e:
        # File paths/errors are local, but never print SSH stderr or key contents.
        message = str(e) if isinstance(e, ValueError) and not isinstance(e, UnicodeError) else "LOCAL_FILE_OR_SSH_SETUP_ERROR"
        print(json.dumps({"status": "ERROR", "code": message}))
        sys.exit(1)

#!/usr/bin/env python3
"""Operator helper: stage code / import a private local OAuth JSON / register public key."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import os

from oauth_setup import validate_client

SOURCE = Path(__file__).resolve().parent
HOST_KEY = "ssh-ed25519 CONFIGURE_LOCAL_PUBLIC_KEY"
HOST_FP = "SHA256:CONFIGURE_LOCAL_FINGERPRINT"
FILES = ("publisher.py", "oauth_setup.py", "client.py", "requirements.txt", "test_publish.py", "drive_browser.py", "drive_client.py", "test_drive_browser.py")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=yes",
       "-o", "ControlMaster=no", "-o", "ControlPath=none", "-o", "IdentityAgent=none", "mestry-s23"]

STAGE = r'''
import base64, hashlib, json, os, pathlib, stat, sys
os.umask(0o077)
home = pathlib.Path.home()
if os.getuid() != 10348 or str(home) != "/data/data/com.termux/files/home":
    raise SystemExit("TERMUX_UID_REQUIRED")
payload = json.load(sys.stdin)
for p in (home/".local", home/".local/lib", home/".local/state"):
    if p.is_symlink(): raise SystemExit("UNSAFE_PARENT")
code = home/".local/lib/mestry-publish"
state = home/".local/state/mestry-publish"
for p in (code, state):
    p.mkdir(parents=True, exist_ok=True, mode=0o700)
    info = p.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise SystemExit("UNSAFE_DIRECTORY")
if (state/"token.json").exists(): raise SystemExit("ACTIVE_INSTALL_NO_AUTOMATIC_RESTAGE")
host_key = pathlib.Path(os.environ["PREFIX"]+"/etc/ssh/ssh_host_ed25519_key.pub").read_text().split()
host_key = " ".join(host_key[:2])
if host_key != payload["host_key"]: raise SystemExit("HOST_KEY_MISMATCH")
allowed = {"publisher.py", "oauth_setup.py", "client.py", "requirements.txt", "test_publish.py", "drive_browser.py", "drive_client.py", "test_drive_browser.py"}
if set(payload["files"]) != allowed: raise SystemExit("FILE_SET_MISMATCH")
hashes = {}
for name, encoded in payload["files"].items():
    raw = base64.b64decode(encoded, validate=True)
    target = code/name
    if target.is_symlink(): raise SystemExit("UNSAFE_CODE_FILE")
    if target.exists() and target.read_bytes() != raw:
        backup = code/(name+".previous")
        if backup.exists() or backup.is_symlink(): raise SystemExit("BACKUP_EXISTS_INSPECT_FIRST")
        backup.write_bytes(target.read_bytes())
        backup.chmod(0o600)
    temp = code/("."+name+".new")
    fd = os.open(temp, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as f: f.write(raw)
    os.replace(temp, target)
    hashes[name] = hashlib.sha256(raw).hexdigest()
sys.path.insert(0,str(code))
from publisher import ACCOUNT, REVIEW_ID, write_private, read_private
config = {"account": ACCOUNT, "review_id": REVIEW_ID}
public_config = {"schema": 1, "known_hosts_line": "[127.0.0.1]:8023 "+host_key,
                 "host_fingerprint": payload["host_fingerprint"]}
for name, value in (("config.json",config),("client-config.json",public_config)):
    target = state/name
    raw = json.dumps(value).encode()
    if target.exists() or target.is_symlink():
        if read_private(target) != raw: raise SystemExit("CONFIG_EXISTS_WITH_DIFFERENT_CONTENT")
    else: write_private(target, raw)
print(json.dumps({"status":"STAGED_INACTIVE", "uid":os.getuid(), "code_sha256":hashes,
                  "credentials_present":(state/"client.json").exists(), "keys_changed":False, "ports_opened":False}))
'''

REGISTER = r'''
import base64, datetime, hashlib, json, os, pathlib, sys
os.umask(0o077)
home = pathlib.Path.home()
if os.getuid() != 10348: raise SystemExit("TERMUX_UID_REQUIRED")
code = home/".local/lib/mestry-publish"
sys.path.insert(0,str(code))
from publisher import read_private, write_private, STATE
obj = json.load(sys.stdin)
raw_key = base64.b64decode(obj["key"], validate=True)
if len(raw_key)!=51 or not raw_key.startswith(bytes.fromhex("0000000b7373682d6564323535313900000020")):
    raise SystemExit("ED25519_PUBLIC_KEY_REQUIRED")
encoded = base64.b64encode(raw_key).decode()
target = home/".ssh/authorized_keys"
previous = read_private(target)
line = ('restrict,from="127.0.0.1,::1",command="/data/data/com.termux/files/usr/bin/python3 -I '+str(code)+'/publisher.py" '
        +'ssh-ed25519 '+encoded+' mestry-horus-publish\n').encode()
if line in previous.splitlines(keepends=True):
    print(json.dumps({"status":"KEY_ALREADY_REGISTERED"})); sys.exit(0)
if encoded.encode() in previous: raise SystemExit("KEY_ALREADY_HAS_OTHER_ACCESS_DO_NOT_REUSE")
if hashlib.sha256(previous).hexdigest() != "31d62780157ee7714a7cc1f145d1825ccda9ab761eda38bf92fb492a8f1c7e59":
    raise SystemExit("AUTHORIZED_KEYS_BASELINE_CHANGED_INSPECT_FIRST")
if len([l for l in previous.splitlines() if l.strip() and not l.startswith(b"#")]) != 2:
    raise SystemExit("EXPECTED_TWO_PRIOR_KEYS")
backup = STATE/("authorized_keys.before-publisher."+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
if backup.exists(): raise SystemExit("BACKUP_EXISTS")
write_private(backup, previous)
if read_private(target) != previous: raise SystemExit("AUTHORIZED_KEYS_CHANGED_DURING_SETUP")
write_private(target, previous+(b"" if previous.endswith(b"\n") else b"\n")+line)
print(json.dumps({"status":"RESTRICTED_KEY_REGISTERED", "previous_keys_preserved":True,
                 "fingerprint":"SHA256:"+base64.b64encode(hashlib.sha256(raw_key).digest()).decode().rstrip("=")}))
'''

def dependencies():
    # Initial interactive authorization is on WSL. S23 runtime is stdlib only.
    base = Path.home() / ".local/share/mestry-publish-setup"
    for parent in (base.parent, base):
        if parent.is_symlink():
            raise SystemExit("UNSAFE_SETUP_PATH")
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    if base.stat().st_uid != os.getuid() or base.stat().st_mode & 0o077:
        raise SystemExit("UNSAFE_SETUP_PERMISSIONS")
    venv = base / "venv"
    if venv.is_symlink():
        raise SystemExit("UNSAFE_SETUP_VENV")
    if not venv.exists():
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)], check=True)
    pip = [sys.executable, "-m", "pip", "--isolated", "--python", str(venv / "bin/python")]
    subprocess.run(pip + ["install", "--only-binary=:all:", "--disable-pip-version-check", "-r", str(SOURCE / "requirements.txt")], check=True)
    subprocess.run(pip + ["check"], check=True)
    subprocess.run([str(venv / "bin/python"), "-c", "from google_auth_oauthlib.flow import InstalledAppFlow; import importlib.metadata as m; print({x:m.version(x) for x in ('google-auth','google-auth-oauthlib')})"], check=True)
    print(json.dumps({"status": "WSL_AUTH_DEPENDENCIES_READY", "oauth_started": False, "ports_opened": False}))


def run_remote(code, payload=None, timeout=45):
    proc = subprocess.run(SSH + ["python3 -c " + shlex.quote(code)],
                          input=json.dumps(payload).encode() if payload is not None else b"",
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    # Only used for non-secret setup output. OAuth/import errors are sanitized remotely.
    sys.stdout.buffer.write(proc.stdout)
    if proc.returncode:
        sys.stderr.buffer.write(proc.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout


def bootstrap_script():
    # Entirely public bootstrap, with a trusted host key obtained through strict WSL SSH.
    return '''#!/bin/sh
set -eu
umask 077
mkdir -p "$HOME/.ssh"
test ! -e "$HOME/.ssh/mestry_publish_known_hosts"
printf '%s\\n' '[127.0.0.1]:8023 @HOST_KEY@' > "$HOME/.ssh/mestry_publish_known_hosts"
python3 - <<'PY'
import base64, hashlib, json, os, pathlib, subprocess
h = pathlib.Path.home()
dest = h/'.local/bin/mestry-publish'
dest.parent.mkdir(parents=True, exist_ok=True)
if dest.exists() or dest.is_symlink(): raise SystemExit('CLIENT_EXISTS_INSPECT_FIRST')
args = ['ssh','-F','/dev/null','-T','-p','8023','-i',str(h/'.ssh/id_ed25519_mestry_publish'),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','IdentityAgent=none','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(h/'.ssh/mestry_publish_known_hosts'),'-o','GlobalKnownHostsFile=/dev/null','-o','ClearAllForwardings=yes','-o','ConnectTimeout=10','u0_a348@127.0.0.1','mestry-publish-bootstrap-v1']
p = subprocess.run(args, check=True, capture_output=True, timeout=30)
obj = json.loads(p.stdout)
raw = base64.b64decode(obj['client_base64'], validate=True)
if len(raw)>20000 or hashlib.sha256(raw).hexdigest()!=obj['client_sha256']: raise SystemExit('BOOTSTRAP_HASH_MISMATCH')
if obj['config']['host_fingerprint']!='@HOST_FP@': raise SystemExit('HOST_PIN_MISMATCH')
fd = os.open(dest, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o700)
with os.fdopen(fd,'wb') as f: f.write(raw)
print('MESTRY_PUBLISH_CLIENT_READY')
PY
'''.replace('@HOST_KEY@', HOST_KEY).replace('@HOST_FP@', HOST_FP)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument("--stage", action="store_true")
    action.add_argument("--dependencies", action="store_true")
    action.add_argument("--import-client", type=Path)
    action.add_argument("--register-key", type=Path)
    action.add_argument("--write-bootstrap", type=Path)
    args = ap.parse_args()
    if args.stage:
        files = {name: base64.b64encode((SOURCE/name).read_bytes()).decode() for name in FILES}
        run_remote(STAGE, {"files": files, "host_key": HOST_KEY, "host_fingerprint": HOST_FP})
    elif args.dependencies:
        dependencies()
    elif args.import_client:
        raw = args.import_client.read_bytes()
        if len(raw) > 100000:
            raise SystemExit("CLIENT_JSON_TOO_LARGE")
        client = validate_client(raw)
        remote = "import sys;sys.path.insert(0,'/data/data/com.termux/files/home/.local/lib/mestry-publish');from oauth_setup import import_client;from publisher import PublishError;import json;\ntry: print(json.dumps(import_client(sys.stdin.buffer.read(100001))))\nexcept Exception: print('CLIENT_IMPORT_FAILED_NO_SECRET_DETAILS');sys.exit(1)"
        run_remote(remote, client)
    elif args.register_key:
        words = args.register_key.read_text().strip().split()
        if len(words) not in (2, 3) or words[0] != "ssh-ed25519":
            raise SystemExit("ONE_ED25519_PUBLIC_KEY_LINE_REQUIRED")
        raw = base64.b64decode(words[1], validate=True)
        if len(raw) != 51 or not raw.startswith(bytes.fromhex("0000000b7373682d6564323535313900000020")):
            raise SystemExit("INVALID_ED25519_PUBLIC_KEY")
        run_remote(REGISTER, {"key": words[1]})
    else:
        with args.write_bootstrap.open("x") as f:
            f.write(bootstrap_script())
        print("Public bootstrap written:", args.write_bootstrap)


if __name__ == "__main__":
    main()

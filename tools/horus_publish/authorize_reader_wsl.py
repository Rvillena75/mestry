#!/usr/bin/env python3
"""Run ONLY in a private user terminal, never via chat tools, tee or evidence log."""
import argparse
import json
import logging
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

SCOPE = "https://www.googleapis.com/auth/drive.readonly"
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
       "-o", "ConnectTimeout=8", "-o", "ControlMaster=no", "-o", "IdentityAgent=none", "mestry-s23"]
REMOTE = r"""
import json,os,pathlib,subprocess,sys
if os.getuid()!=10348 or subprocess.check_output(['/system/bin/getprop','ro.product.model'],text=True).strip()!='SM-S918B':
 raise SystemExit('TERMUX_S23_REQUIRED')
sys.path.insert(0,str(pathlib.Path.home()/'.local/lib/mestry-publish'))
from document_reader import prepare_authorization,commit_authorization
from publisher import PublishError
try:
 value=json.load(sys.stdin)
 result=prepare_authorization() if value['action']=='prepare' else commit_authorization(value)
 print(json.dumps(result))
except PublishError as error:
 print(json.dumps({'status':'ERROR','code':str(error)}));sys.exit(1)
except Exception:
 print(json.dumps({'status':'ERROR','code':'READER_SETUP_FAILED_NO_PRIVATE_DETAILS'}));sys.exit(1)
"""


def remote(payload):
    result = subprocess.run(SSH + ["python -B -c " + shlex.quote(REMOTE)],
                            input=json.dumps(payload).encode(), capture_output=True, timeout=150)
    try:
        value = json.loads(result.stdout)
    except Exception:
        raise ValueError("READER_SSH_FAILED_NO_PRIVATE_DETAILS") from None
    if result.returncode or value.get("status") == "ERROR":
        code = value.get("code", "")
        raise ValueError(code if re.fullmatch("[A-Z0-9_]+", code) else "READER_SETUP_FAILED")
    return value


def authorize(client, account):
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_config(client, [SCOPE], autogenerate_code_verifier=True)
    try:
        creds = flow.run_local_server(host="127.0.0.1", port=53682, open_browser=False,
            timeout_seconds=180, authorization_prompt_message="Abre este enlace sólo en el navegador del PC: {url}",
            success_message="MESTRY recibió el consentimiento de lectura. Vuelve a la terminal.",
            access_type="offline", prompt="consent", include_granted_scopes="false", login_hint=account)
    except Exception as error:
        reason = getattr(error, "error", None)
        if reason in {"access_denied", "invalid_scope", "invalid_client", "unauthorized_client"}:
            raise ValueError("READER_GOOGLE_" + reason.upper()) from None
        if isinstance(error, Warning):
            raise ValueError("READER_GOOGLE_SCOPE_DIFFERENT") from None
        raise ValueError("READER_CONSENT_NOT_COMPLETED") from None
    if creds is None:
        raise ValueError("READER_CONSENT_NOT_COMPLETED")
    scopes = flow.oauth2session.token.get("scope", [])
    if isinstance(scopes, str):
        scopes = scopes.split()
    if set(scopes) != {SCOPE} or not creds.refresh_token:
        raise ValueError("READER_EXACT_READONLY_SCOPE_REQUIRED")
    return json.loads(creds.to_json())


def save_receipt(result):
    receipt = Path.home() / ".local/state/mestry-reader-setup/result.json"
    receipt.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    receipt.write_text(json.dumps(result))
    receipt.chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-loopback-53682", action="store_true")
    args = parser.parse_args()
    if not args.allow_loopback_53682:
        raise ValueError("READER_CALLBACK_APPROVAL_REQUIRED")
    os.umask(0o077)
    logging.disable(logging.CRITICAL)
    setup = remote({"action": "prepare"})
    print("MESTRY: lector de sólo lectura. El publicador conserva su token.", flush=True)
    print("En Google, concede lectura de Drive. MESTRY sincroniza sólo la raíz ya seleccionada.", flush=True)
    token = authorize(setup["client"], setup["account"])
    result = remote({"action": "commit", "roots": setup["roots"], "token": token})
    # Only this safe receipt is persisted on WSL; never client JSON, code or tokens.
    save_receipt(result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        code = str(error) if type(error) is ValueError and re.fullmatch("[A-Z0-9_]+", str(error)) else "PRIVATE_READER_SETUP_FAILED"
        result = {"status": "ERROR", "code": code}
        save_receipt(result)
        print(json.dumps(result), flush=True)
        sys.exit(1)

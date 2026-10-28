#!/usr/bin/env python3
"""Private operator setup. Never invoked by the forced-command SSH capability."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import types

from publisher import (ACCOUNT, REVIEW_ID, SCOPE, STATE, Drive, PublishError,
                       journal, prepare_folder, read_config, read_private,
                       state_dir, write_private)


def validate_client(raw):
    try:
        value = json.loads(raw)
        client = value["installed"]
        if set(value) != {"installed"} or not isinstance(client, dict):
            raise ValueError
        if (client.get("auth_uri") != "https://accounts.google.com/o/oauth2/auth"
                or client.get("token_uri") != "https://oauth2.googleapis.com/token"
                or not re.fullmatch(r"[A-Za-z0-9._-]+\.apps\.googleusercontent\.com", client.get("client_id", ""))
                or not isinstance(client.get("client_secret"), str) or not client["client_secret"]
                or "http://localhost" not in client.get("redirect_uris", [])):
            raise ValueError
        return value
    except (ValueError, TypeError, KeyError):
        raise PublishError("DESKTOP_GOOGLE_CLIENT_JSON_REQUIRED") from None


def import_client(raw):
    value = validate_client(raw)
    state_dir()
    dest = STATE / "client.json"
    if dest.exists() or dest.is_symlink() or (STATE / "token.json").exists():
        if read_private(dest) == json.dumps(value).encode():
            return {"status": "CLIENT_ALREADY_IMPORTED"}
        raise PublishError("CLIENT_EXISTS_NO_REPLACEMENT")
    write_private(dest, json.dumps(value).encode())
    return {"status": "CLIENT_IMPORTED", "account": ACCOUNT, "scopes": [SCOPE]}


def authorize(allow_loopback, client):
    """WSL only, invoked privately by the operator through authorize_wsl.py."""
    if not allow_loopback:
        raise PublishError("EXPLICIT_APPROVAL_FOR_TEMPORARY_LOOPBACK_53682_REQUIRED")
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_config(client, [SCOPE], autogenerate_code_verifier=True)
    print("Abre Google en el navegador del PC; plazo 180 segundos. Cuenta: " + ACCOUNT, flush=True)
    try:
        creds = flow.run_local_server(
            host="127.0.0.1", port=53682, open_browser=False, timeout_seconds=180,
            authorization_prompt_message="Abre este enlace solo en tu navegador del PC: {url}",
            success_message="MESTRY recibió la autorización. Puedes cerrar esta pestaña y volver a WSL.",
            access_type="offline", prompt="consent", include_granted_scopes="false",
            login_hint=ACCOUNT)
    except Exception:
        raise PublishError("OAUTH_NOT_COMPLETED_RETRY_LOCALLY") from None
    granted = flow.oauth2session.token.get("scope", [])
    if isinstance(granted, str):
        granted = granted.split()
    if set(granted) != {SCOPE} or not creds.refresh_token:
        raise PublishError("OAUTH_SCOPE_OR_REFRESH_TOKEN_MISMATCH")
    # Verify the account before persisting a usable token or any Drive mutation.
    checker = Drive.__new__(Drive)
    checker.creds = creds
    import urllib.request
    from publisher import NoRedirect
    checker.opener = urllib.request.build_opener(NoRedirect())
    if checker.account().lower() != ACCOUNT:
        raise PublishError("DRIVE_ACCOUNT_MISMATCH_TOKEN_NOT_SAVED")
    return json.loads(creds.to_json())


def import_token(raw):
    read_config()
    token = json.loads(raw)
    client = validate_client(read_private(STATE / "client.json"))["installed"]
    if (set(token.get("scopes", [])) != {SCOPE}
            or token.get("token_uri") != "https://oauth2.googleapis.com/token"
            or token.get("client_id") != client["client_id"] or token.get("client_secret") != client["client_secret"]
            or not all(isinstance(token.get(k), str) and token[k] for k in ("token", "refresh_token", "expiry"))):
        raise PublishError("TOKEN_CLIENT_OR_SCOPE_MISMATCH")
    if (STATE / "token.json").exists() or (STATE / "token.json").is_symlink():
        raise PublishError("TOKEN_EXISTS_NO_REPLACEMENT")
    checker = Drive.__new__(Drive)
    checker.creds = types.SimpleNamespace(token=token["token"])
    import urllib.request
    from publisher import NoRedirect
    checker.opener = urllib.request.build_opener(NoRedirect())
    if checker.account().lower() != ACCOUNT:
        raise PublishError("DRIVE_ACCOUNT_MISMATCH_TOKEN_NOT_SAVED")
    write_private(STATE / "token.json", json.dumps(token).encode())
    return {"status": "OAUTH_AUTHORIZED_ON_S23", "account": ACCOUNT, "scopes": [SCOPE]}


def main():
    os.umask(0o077)
    if os.getuid() != 10348 or str(Path.home()) != "/data/data/com.termux/files/home":
        raise PublishError("TERMUX_UID_REQUIRED")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["import-client", "import-token", "prepare-folder", "status"])
    a = p.parse_args()
    if a.action == "import-client":
        raw = sys.stdin.buffer.read(100001)
        if len(raw) > 100000:
            raise PublishError("CLIENT_JSON_TOO_LARGE")
        return import_client(raw)
    if a.action == "import-token":
        raw = sys.stdin.buffer.read(100001)
        if len(raw) > 100000:
            raise PublishError("TOKEN_TOO_LARGE")
        return import_token(raw)
    read_config()
    if a.action == "prepare-folder":
        with journal() as conn:
            return prepare_folder(Drive(), conn)
    return {"status": "LOCAL_SETUP_STATUS", "client_present": (STATE / "client.json").is_file(),
            "token_present": (STATE / "token.json").is_file(), "review_id": REVIEW_ID}


if __name__ == "__main__":
    try:
        result = main()
    except PublishError as e:
        print(json.dumps({"status": "ERROR", "code": str(e)}))
        sys.exit(1)
    except Exception:
        print(json.dumps({"status": "ERROR", "code": "SETUP_ERROR_NO_SECRET_DETAILS"}))
        sys.exit(1)
    print(json.dumps(result))

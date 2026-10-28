#!/usr/bin/env python3
"""User-run, one-time OAuth with official library. No token is written on WSL."""
import argparse
import json
import os
from pathlib import Path
import sys

from install import SOURCE, run_remote
from oauth_setup import authorize, validate_client
from publisher import PublishError, SCOPE


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client_json", type=Path)
    parser.add_argument("--allow-loopback-53682", action="store_true")
    args = parser.parse_args()
    if not args.allow_loopback_53682:
        raise PublishError("EXPLICIT_APPROVAL_FOR_TEMPORARY_LOOPBACK_53682_REQUIRED")
    path = args.client_json.resolve(strict=True)
    if path.is_relative_to(SOURCE.parents[1]):
        raise PublishError("CLIENT_JSON_MUST_STAY_OUTSIDE_PROJECT")
    raw = path.read_bytes()
    if len(raw) > 100000:
        raise PublishError("CLIENT_JSON_TOO_LARGE")
    client = validate_client(raw)
    # Import the client without logging its contents or sending it via argv.
    command = ("import sys;sys.path.insert(0,'/data/data/com.termux/files/home/.local/lib/mestry-publish');"
               "from oauth_setup import import_client;import json;\n"
               "try: print(json.dumps(import_client(sys.stdin.buffer.read(100001))))\n"
               "except Exception: print('CLIENT_IMPORT_FAILED_NO_SECRET_DETAILS');sys.exit(1)")
    run_remote(command, client)
    status = run_remote("import sys;sys.path.insert(0,'/data/data/com.termux/files/home/.local/lib/mestry-publish');from oauth_setup import main;sys.argv=['oauth_setup.py','status'];import json;print(json.dumps(main()))")
    if json.loads(status).get("token_present"):
        raise PublishError("TOKEN_EXISTS_USE_EXISTING_AUTHORIZATION")
    token = authorize(True, client)
    command = ("import sys;sys.path.insert(0,'/data/data/com.termux/files/home/.local/lib/mestry-publish');"
               "from oauth_setup import import_token;import json;\n"
               "try: print(json.dumps(import_token(sys.stdin.buffer.read(100001))))\n"
               "except Exception: print('TOKEN_IMPORT_FAILED_RETRY_PRIVATELY_NO_SECRET_DETAILS');sys.exit(1)")
    run_remote(command, token)
    print(json.dumps({"status": "S23_AUTH_SETUP_COMPLETE", "scope": SCOPE,
                      "token_saved_on_wsl": False, "publication_performed": False}))


if __name__ == "__main__":
    try:
        main()
    except PublishError as e:
        print(json.dumps({"status": "ERROR", "code": str(e)}))
        sys.exit(1)
    except Exception:
        # HTTP/OAuth exceptions can include tokens or the callback URL.
        print(json.dumps({"status": "ERROR", "code": "PRIVATE_AUTHORIZATION_FAILED_NO_SECRET_DETAILS"}))
        sys.exit(1)

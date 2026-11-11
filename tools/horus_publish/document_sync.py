#!/usr/bin/env python3
"""Private operator entrypoint: selected-root synchronization, status and retrieval."""
import argparse
import json
import sys
from pathlib import Path

from publisher import (ACCOUNT, STATE, Drive, PublishError, read_config,
                       require_account)
from drive_browser import load_state
from drive_sync import DriveAPI, selected_store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["sync", "status", "read", "list", "clear", "history"])
    parser.add_argument("--root-id", required=True)
    parser.add_argument("--file-id")
    parser.add_argument("--version", help="Retrieve a retained remote version as an explicitly historical snapshot")
    parser.add_argument("--folder-id")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--reconcile", action="store_true", help="Re-inventory selection without deleting retained objects")
    args = parser.parse_args()
    read_config()
    state = load_state(STATE)
    if args.root_id not in state["enabled"]:
        raise PublishError("DRIVE_FOLDER_DISABLED")
    marker = STATE / "reader/selection.json"
    if marker.exists() or marker.is_symlink():
        from document_reader import load_selection
        if args.root_id not in load_selection()["roots"]:
            raise PublishError("READER_ROOT_NOT_SELECTED")
    if args.offline and args.action == "sync":
        raise PublishError("SYNC_NETWORK_REQUIRED")
    with selected_store(STATE, ACCOUNT, args.root_id) as store:
        if args.action == "status":
            return store.status()
        if args.action == "clear":
            return store.clear()
        if args.reconcile:
            with store.db:
                store.set("rescan", 1)
        api = None
        if not args.offline:
            from document_reader import open_reader
            drive = open_reader()
            require_account(drive)
            api = DriveAPI(drive)
        if args.action == "sync":
            return store.sync(api)
        if args.action in {"read", "history"}:
            if not args.file_id:
                raise PublishError("SYNC_FILE_ID_REQUIRED")
            if args.action == "history":
                if not args.offline:
                    store.read(api, args.file_id)
                return {"status": "OK", "versions": store.history(args.file_id)}
            if args.version:
                return store.read_version(api, args.file_id, args.version, offline=args.offline)
            return store.read(api, args.file_id, offline=args.offline)
        if not args.offline:
            store.sync(api)
        return {"status": "OK", "offline": args.offline, "freshness": "cached_unverified",
                "files": store.listing(args.folder_id or args.root_id),
                "sync": store.status()}


if __name__ == "__main__":
    try:
        print(json.dumps(main(), ensure_ascii=False))
    except Exception as error:
        code = str(error) if isinstance(error, PublishError) else "SYNC_FAILED"
        # Never echo exceptions carrying URLs, OAuth or document bytes.
        if not code.replace("_", "").isalnum() or not code.isupper():
            code = "SYNC_FAILED"
        print(json.dumps({"status": "ERROR", "code": code}))
        sys.exit(1)

#!/usr/bin/env python3
"""Read a previously verified synthetic revision through the installed Termux runtime."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time


def read_fixture(p, *, allow_restored_location=False):
    result = dict(marker='S23_DRIVE_EXISTING_READ', utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  remote_writes=False, content_exported=False, authentication_verified=False,
                  ordinary_refresh_performed=False)
    try:
        p.read_config()
        database = p.STATE / 'journal.sqlite3'
        p.private_path(database)
        with sqlite3.connect(database.as_uri()+'?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute('SELECT file_id,digest,name FROM publication WHERE verified=1 ORDER BY seq DESC LIMIT 1').fetchone()
            folder = connection.execute('SELECT file_id FROM folder WHERE singleton=1').fetchone()
        if row is None or folder is None:
            raise p.PublishError('EXISTING_VERIFIED_FIXTURE_REQUIRED')
        class ObservedDrive(p.Drive):
            def refresh(self, obj):
                updated = super().refresh(obj)
                result['ordinary_refresh_performed'] = True
                return updated
        drive = ObservedDrive()
        p.require_account(drive)
        result['authentication_verified'] = True
        folder_meta = drive.metadata(folder['file_id'])
        if folder_meta.get('trashed') is True:
            raise p.PublishError('EXISTING_FIXTURE_FOLDER_IN_TRASH')
        # This only reads the same journal IDs; publication retains its own guard.
        p.require_folder(folder_meta, folder['file_id'], ready=False)
        destination_ready = folder_meta.get('parents') == [p.REVIEW_ID]
        result['publication_destination_ready'] = destination_ready
        result['restored_location_read_only'] = not destination_ready and allow_restored_location
        if not destination_ready and not allow_restored_location:
            raise p.PublishError('DRIVE_FOLDER_MOVE_TO_REVIEW_REQUIRED')
        before = drive.metadata(row['file_id'])
        if before.get('trashed') is True:
            raise p.PublishError('EXISTING_FIXTURE_IN_TRASH')
        p.require_private(before)
        if before.get('parents') != [folder['file_id']] or before.get('name') != row['name']:
            raise p.PublishError('EXISTING_FIXTURE_METADATA_MISMATCH')
        content = drive.download(row['file_id'])
        after = drive.metadata(row['file_id'])
        p.require_private(after)
        digest = hashlib.sha256(content).hexdigest()
        if before != after or digest != row['digest']:
            raise p.PublishError('EXISTING_FIXTURE_CHANGED_PRESERVED')
        result.update(status='PASS', scope='drive.file', bytes=len(content), sha256=digest,
                      metadata_stable=True, existing_revision_verified=True)
    except Exception as error:
        code = str(error) if isinstance(error, p.PublishError) else 'READ_FAILED_NO_PRIVATE_DETAILS'
        result.update(status='BLOCKED', reason=code if re.fullmatch('[A-Z_0-9]+', code)
                      else 'READ_FAILED_NO_PRIVATE_DETAILS')
    return result


def main():
    if os.getuid() != 10348 or str(Path.home()) != '/data/data/com.termux/files/home':
        print(json.dumps(dict(status='BLOCKED', reason='EXISTING_TERMUX_PROFILE_REQUIRED')))
        return 1
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-restored-location', action='store_true',
        help='Read the same journal fixture after an explicitly authorized restore; never changes publication configuration')
    args = parser.parse_args()
    # Deployment-specific account and IDs stay in the existing private runtime.
    sys.path.insert(0, str(Path.home()/'.local/lib/mestry-publish'))
    try:
        publisher = importlib.import_module('publisher')
        result = read_fixture(publisher, allow_restored_location=args.allow_restored_location)
    except Exception:
        result = dict(status='BLOCKED', reason='INSTALLED_RUNTIME_UNAVAILABLE')
    print(json.dumps(result))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

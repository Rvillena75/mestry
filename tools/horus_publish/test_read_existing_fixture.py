import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import types
import unittest

from read_existing_fixture import read_fixture


class ExistingFixtureTests(unittest.TestCase):
    def publisher(self, *, trashed=False, changed=False, moved=False):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        state = Path(directory.name)
        content = b'existing synthetic revision\n'
        with sqlite3.connect(state/'journal.sqlite3') as connection:
            connection.executescript('CREATE TABLE folder(singleton INTEGER,file_id TEXT);'
                'CREATE TABLE publication(seq INTEGER,file_id TEXT,digest TEXT,name TEXT,verified INTEGER);')
            connection.execute('INSERT INTO folder VALUES(1,?)', ('private-folder-fixture',))
            connection.execute('INSERT INTO publication VALUES(1,?,?,?,1)',
                ('private-file-fixture', hashlib.sha256(content).hexdigest(), 'revision.md'))
        calls = []
        class PublishError(Exception):
            pass
        class Drive:
            def __init__(self):
                self.refresh({})
            def refresh(self, value):
                calls.append('refresh')
                return value
            def metadata(self, file_id):
                calls.append('metadata')
                return {'trashed': trashed, 'name': 'revision.md', 'parents': (['other-parent'] if moved else ['review-parent-fixture']) if file_id == 'private-folder-fixture' else ['private-folder-fixture']}
            def download(self, file_id):
                calls.append('download')
                return b'changed remote revision' if changed else content
        module = types.SimpleNamespace(STATE=state, REVIEW_ID='review-parent-fixture', PublishError=PublishError, Drive=Drive,
            read_config=lambda: None, private_path=lambda p: None, require_account=lambda d: None,
            require_folder=lambda m, i, **kwargs: None, require_private=lambda m: None)
        return module, calls

    def test_trashed_pilot_stops_before_content_download(self):
        publisher, calls = self.publisher(trashed=True)
        result = read_fixture(publisher)
        self.assertEqual(result['reason'], 'EXISTING_FIXTURE_FOLDER_IN_TRASH')
        self.assertTrue(result['authentication_verified'])
        self.assertTrue(result['ordinary_refresh_performed'])
        self.assertNotIn('download', calls)

    def test_remote_edit_is_preserved_and_not_reported_as_verified(self):
        publisher, calls = self.publisher(changed=True)
        result = read_fixture(publisher)
        self.assertEqual(result['reason'], 'EXISTING_FIXTURE_CHANGED_PRESERVED')
        self.assertFalse(result['remote_writes'])
        self.assertNotIn('sha256', result)

    def test_restored_location_requires_opt_in_and_does_not_enable_publication(self):
        publisher, calls = self.publisher(moved=True)
        result = read_fixture(publisher)
        self.assertEqual(result['reason'], 'DRIVE_FOLDER_MOVE_TO_REVIEW_REQUIRED')
        self.assertNotIn('download', calls)
        result = read_fixture(publisher, allow_restored_location=True)
        self.assertEqual(result['status'], 'PASS')
        self.assertFalse(result['publication_destination_ready'])
        self.assertTrue(result['restored_location_read_only'])
        self.assertEqual(publisher.REVIEW_ID, 'review-parent-fixture')

    def test_existing_bytes_are_verified_without_exporting_ids_or_content(self):
        publisher, calls = self.publisher()
        result = read_fixture(publisher)
        self.assertEqual(result['status'], 'PASS')
        self.assertTrue(result['metadata_stable'])
        self.assertFalse(result['remote_writes'])
        self.assertFalse(result['content_exported'])
        self.assertEqual(calls.count('download'), 1)
        self.assertNotIn('private-file-fixture', json.dumps(result))
        self.assertNotIn('existing synthetic revision', json.dumps(result))


if __name__ == '__main__':
    unittest.main()

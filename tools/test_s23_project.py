"""Release overlays preserve device-local code and reject unsafe inputs."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import s23_project


class ReleaseOverlayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.old = self.base / 'installed'
        (self.old / 'src').mkdir(parents=True)
        self.entry = ("const root = '/workspace/projects/fixture';\n"
                      "async function main() {\n  const backend = {};\n  const bridge = new BridgeServer({});\n}\n")
        (self.old / 'src/mestry-entry.mjs').write_text(self.entry)
        (self.old / 'src/preserved.mjs').write_text('// device-local existing code\n')
        (self.old / 'horus_control.py').write_text("launch(cwd='/workspace/projects/fixture')\n")
        self.manifest()

    def manifest(self):
        files = {str(p.relative_to(self.old)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.old.rglob('*') if p.is_file() and p.name != 'manifest.json'}
        (self.old / 'manifest.json').write_text(json.dumps({'files': files, 'version': 'fixture'}))

    def test_overlay_preserves_original_and_unrelated_members(self):
        target = self.base / 'candidate'
        result = s23_project.compose_release(self.old, target, self.base / 'project')
        self.assertEqual((self.old / 'src/mestry-entry.mjs').read_text(), self.entry)
        self.assertEqual((target / 'src/preserved.mjs').read_bytes(), (self.old / 'src/preserved.mjs').read_bytes())
        self.assertIn('guardBackend', (target / 'src/mestry-entry.mjs').read_text())
        self.assertEqual(result, hashlib.sha256((target / 'manifest.json').read_bytes()).hexdigest())

    def test_symlink_in_installed_release_is_rejected(self):
        (self.old / 'src/link.mjs').symlink_to(self.old / 'src/preserved.mjs')
        self.manifest()
        with self.assertRaisesRegex(ValueError, 'RELEASE_MEMBERS_CHANGED'):
            s23_project.compose_release(self.old, self.base / 'candidate', self.base / 'project')

    def test_changed_installed_member_is_rejected(self):
        (self.old / 'src/preserved.mjs').write_text('// unexpected change\n')
        with self.assertRaisesRegex(ValueError, 'RELEASE_HASH_MISMATCH'):
            s23_project.compose_release(self.old, self.base / 'candidate', self.base / 'project')

    def test_existing_destination_is_preserved(self):
        target = self.base / 'candidate'
        target.mkdir()
        with self.assertRaisesRegex(ValueError, 'DESTINATION_EXISTS'):
            s23_project.compose_release(self.old, target, self.base / 'project')
        self.assertEqual(list(target.iterdir()), [])


if __name__ == '__main__':
    unittest.main()

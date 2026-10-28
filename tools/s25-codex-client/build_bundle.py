#!/usr/bin/env python3
"""Build a code-only Horus bundle from the isolated, pinned candidate sources."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

UPSTREAM = '538d65f67e34907789237fc71f56e8ca95d9f3cb'


def build(source, output):
    lock = json.loads((source / 'package-lock.json').read_text())
    dependency = lock['packages']['node_modules/ws']
    version = dependency['version']
    # Verify the mirror-downloaded dependency against the official npm registry.
    with urllib.request.urlopen('https://registry.npmjs.org/ws/' + version, timeout=20) as response:
        official = json.load(response)
    if dependency['integrity'] != official['dist']['integrity']:
        raise ValueError('OFFICIAL_DEPENDENCY_INTEGRITY_MISMATCH')
    files = {}
    for path in (source / 'src').rglob('*.mjs'):
        if str(path.relative_to(source)) in ('src/index.mjs', 'src/backends/mock.mjs'):
            continue  # The phone bundle has one entry and no synthetic backend.
        files[str(path.relative_to(source))] = path.read_bytes()
    files['src/mestry-drive-client.py'] = (source / 'src/mestry-drive-client.py').read_bytes()
    for path in (source / 'node_modules/ws').rglob('*'):
        if path.is_symlink():
            raise ValueError('UNEXPECTED_DEPENDENCY_SYMLINK')
        if path.is_file():
            files[str(path.relative_to(source))] = path.read_bytes()
    for name in ['package.json', 'package-lock.json', 'LICENSE']:
        files[name] = (source / name).read_bytes()
    here = Path(__file__).resolve().parent
    for name in ['horus_control.py', 'horus_install.py', 'horus_upgrade.py']:
        files[name] = (here / name).read_bytes()
    files['MESTRY_ORIGIN.json'] = (json.dumps({
        'upstream': 'https://github.com/chenhaoc/codex-remote-control',
        'commit': UPSTREAM, 'license': 'GPL-3.0-only', 'personal_patch': 'mestry-pilot5',
        'ws_version': version, 'official_npm_integrity_verified': True,
        'no_oauth_or_login_material': True, 'runtime': 'existing Horus Node/Codex only',
    }, indent=2) + '\n').encode()
    manifest = {'version': 'mestry-pilot5', 'base_commit': UPSTREAM,
                'files': {name: hashlib.sha256(body).hexdigest() for name, body in sorted(files.items())}}
    files['manifest.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with output.open('xb') as destination:
        # Stable tar metadata, code only; gzip header timestamp is irrelevant to validation.
        with tarfile.open(fileobj=destination, mode='w:gz') as archive:
            for name, body in sorted(files.items()):
                relative = Path(name)
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('UNSAFE_MEMBER')
                member = tarfile.TarInfo(name)
                member.size = len(body)
                member.mode = 0o600
                member.mtime = 0
                archive.addfile(member, io.BytesIO(body))
    return {'bundle': str(output), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'bytes': output.stat().st_size, 'file_count': len(files), 'ws_version': version,
            'official_npm_integrity_verified': True,
            'manifest_sha256': hashlib.sha256(files['manifest.json']).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output)))

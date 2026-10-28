#!/usr/bin/env python3
"""Install a hash-checked public-code bundle inside the existing Horus profile."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


def install(source):
    if str(Path.home()) != '/home/horus' or os.uname().machine != 'aarch64':
        raise ValueError('HORUS_SSH_PROFILE_REQUIRED')
    os.umask(0o077)
    manifest_bytes = (source / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    expected = manifest['files']
    actual = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file() and p.relative_to(source) != Path('manifest.json')}
    if actual != set(expected):
        raise ValueError('FILE_SET_MISMATCH')
    for name, digest in expected.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('UNSAFE_MEMBER')
        path = source / relative
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('FILE_HASH_MISMATCH')
    base = Path.home() / '.local/lib/mestry-s25-pilot'
    release = base / 'releases' / hashlib.sha256(manifest_bytes).hexdigest()[:20]
    controller = Path.home() / '.local/bin/mestry-bridge'
    pointer = base / 'current.json'
    if controller.exists() or controller.is_symlink() or pointer.exists() or pointer.is_symlink():
        raise ValueError('EXISTING_INSTALL_NO_OVERWRITE')
    if base.is_symlink() or (base.exists() and base.stat().st_mode & 0o077):
        raise ValueError('PRIVATE_INSTALL_DIRECTORY_REQUIRED')
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    release.parent.mkdir(mode=0o700, exist_ok=True)
    if release.exists():
        raise ValueError('RELEASE_EXISTS_NO_OVERWRITE')
    shutil.copytree(source, release)
    for path in release.rglob('*'):
        os.chmod(path, 0o700 if path.is_dir() else 0o600)
    controller.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # The wrapper points at this versioned release, without copying any login data.
    with controller.open('x') as stream:
        stream.write('#!/bin/sh\nexec /usr/bin/python3 "' + str(release / 'horus_control.py') + '" "$@"\n')
    controller.chmod(0o700)
    with pointer.open('x') as stream:
        stream.write(json.dumps({'directory': str(release), 'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest()}) + '\n')
    pointer.chmod(0o600)
    print('MESTRY_HORUS_BRIDGE_INSTALLED_NO_PORT_OPENED')
    print('Version=' + manifest['version'])


if __name__ == '__main__':
    try:
        install(Path(__file__).resolve().parent)
    except Exception:
        print('MESTRY_INSTALL_FAILED_NO_RAW_OUTPUT', file=sys.stderr)
        raise SystemExit(1)

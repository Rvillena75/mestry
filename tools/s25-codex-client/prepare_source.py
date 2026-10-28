#!/usr/bin/env python3
"""Reproduce the private pilot sources from a pinned archive and reviewed patch."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import urllib.request


def prepare(archive, destination):
    here = Path(__file__).resolve().parent
    pins = json.loads((here / 'source-pins.json').read_text())
    patch = (here / 'mestry-pilot1.patch').read_bytes()
    if hashlib.sha256(archive.read_bytes()).hexdigest() != pins['upstream_archive_sha256']:
        raise ValueError('UPSTREAM_ARCHIVE_HASH_MISMATCH')
    if hashlib.sha256(patch).hexdigest() != pins['patch_sha256']:
        raise ValueError('PATCH_HASH_MISMATCH')
    if destination.exists():
        raise ValueError('DESTINATION_EXISTS_NO_OVERWRITE')
    destination.mkdir(parents=True, mode=0o700)
    with tarfile.open(archive, 'r:gz') as source:
        members = source.getmembers()
        if len(members) > 5000 or sum(member.size for member in members) > 64_000_000:
            raise ValueError('ARCHIVE_LIMIT_EXCEEDED')
        prefix = None
        for member in members:
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts or not (member.isdir() or member.isfile()):
                raise ValueError('UNSAFE_ARCHIVE_MEMBER')
            if prefix is None:
                prefix = relative.parts[0]
            if relative.parts[0] != prefix:
                raise ValueError('MULTIPLE_SOURCE_ROOTS')
            if len(relative.parts) == 1:
                continue
            target = destination.joinpath(*relative.parts[1:])
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True, mode=0o700)
            else:
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                with source.extractfile(member) as body, target.open('xb') as output:
                    output.write(body.read())
                target.chmod(0o700 if member.mode & 0o111 else 0o600)
    result = subprocess.run(['patch', '--batch', '--forward', '-p1', '-d', str(destination)], input=patch,
                            capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError('PATCH_APPLICATION_FAILED')
    replacement = pins['wrapper_jar']
    with urllib.request.urlopen(replacement['url'], timeout=25) as response:
        body = response.read(1_000_000)
    if hashlib.sha256(body).hexdigest() != replacement['sha256']:
        raise ValueError('OFFICIAL_WRAPPER_HASH_MISMATCH')
    (destination / replacement['path']).write_bytes(body)
    for name, expected in pins['changed_text_files'].items():
        path = destination / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if digest != expected['after_sha256']:
            raise ValueError('REPRODUCED_FILE_HASH_MISMATCH')
    return {'status': 'PINNED_PATCHED_SOURCE_REPRODUCED', 'destination': str(destination),
            'upstream_commit': pins['upstream_commit'], 'verified_changed_files': len(pins['changed_text_files']),
            'wrapper_jar_verified': True, 'code_executed': False, 'dependencies_installed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.archive, args.destination)))

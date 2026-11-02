#!/usr/bin/env python3
"""Admit this checkout into the existing Horus bridge without replacing accounts."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile

from work_session import Session, Blocked, digest, now, private_dir, write_private

ROOT = Path(__file__).resolve().parent.parent


def upgrade_module():
    source = ROOT / 'tools/s25-codex-client/horus_upgrade.py'
    spec = importlib.util.spec_from_file_location('mestry_reviewed_upgrade', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compose_release(previous, destination, root):
    """Code-only overlay on the verified device-local release, not public examples."""
    if destination.exists():
        raise ValueError('DESTINATION_EXISTS')
    if not root.is_absolute() or root.resolve() != root:
        raise ValueError('CANONICAL_PROJECT_REQUIRED')
    upgrade = upgrade_module()
    old_manifest = upgrade.verify_release(previous)
    entry = (previous / 'src/mestry-entry.mjs').read_text()
    control = (previous / 'horus_control.py').read_text()
    if 'guardBackend' in entry:
        raise ValueError('PROJECT_ALREADY_ADMITTED_REVIEW_BEFORE_UPGRADE')
    roots = re.findall(r'^const root = (.+);$', entry, re.M)
    if len(roots) != 1 or not re.fullmatch(r"['\"]/workspace/projects/[A-Za-z0-9_-]+['\"]", roots[0]):
        raise ValueError('INSTALLED_ENTRY_ROOT_REVIEW_REQUIRED')
    old_root = roots[0][1:-1]
    anchor = '\n  const bridge = new BridgeServer('
    if entry.count(anchor) != 1 or control.count("cwd='" + old_root + "'") != 1:
        raise ValueError('INSTALLED_LAYOUT_REVIEW_REQUIRED')
    entry = "import { ProjectGate, guardBackend } from './mestry-project-gate.mjs';\n" + entry
    entry = entry.replace('const root = ' + roots[0] + ';', 'const root = ' + json.dumps(str(root)) + ';')
    entry = entry.replace(anchor, '\n  guardBackend(backend, {root, gate: new ProjectGate(root, {applyOnEntry: true})});' + anchor)
    control = control.replace("cwd='" + old_root + "'", 'cwd=' + repr(str(root)))
    shutil.copytree(previous, destination)
    (destination / 'src/mestry-entry.mjs').write_text(entry)
    (destination / 'horus_control.py').write_text(control)
    shutil.copyfile(ROOT / 'tools/project-gate.mjs', destination / 'src/mestry-project-gate.mjs')
    manifest = json.loads(old_manifest)
    manifest['version'] = 'mestry-h3-project-sessions'
    manifest['files'] = {str(p.relative_to(destination)): digest(p.read_bytes())
                         for p in sorted(destination.rglob('*')) if p.is_file() and p.relative_to(destination) != Path('manifest.json')}
    (destination / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    for p in destination.rglob('*'):
        p.chmod(0o700 if p.is_dir() else 0o600)
    upgrade.verify_release(destination)
    return digest((destination / 'manifest.json').read_bytes())


def run(args, timeout=35):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise ValueError('LOCAL_COMMAND_FAILED_NO_PRIVATE_OUTPUT')
    return result.stdout


def expected_profile():
    if Path.home() != Path('/home/horus') or os.getuid() != 1000 or platform.machine() != 'aarch64':
        raise ValueError('EXPECTED_HORUS_PROFILE_REQUIRED')
    if ROOT != Path('/workspace/projects/mestry') or ROOT.is_symlink():
        raise ValueError('EXPECTED_PROJECT_CHECKOUT_REQUIRED')


def verify():
    expected_profile()
    session = Session(ROOT)
    session.load()
    with session.lock():
        if session.status() or session.state.get('phase') in ('running', 'recovery_required'):
            raise ValueError('CLEAN_FREE_PROJECT_REQUIRED')
        results = session.validate('HEAD')
        session.record('verified', phase='idle')
    return {'target': platform.machine(), 'head': session.text('rev-parse', 'HEAD'), 'validation': results}


def activate(head):
    expected_profile()
    session = Session(ROOT)
    session.load()
    upgrade = upgrade_module()
    home = Path.home()
    state = home / '.local/state/mestry-s25-client'
    base = home / '.local/lib/mestry-s25-pilot'
    keeper = home / '.local/bin/mestry-keepalive'
    keeper_source = home / '.local/lib/mestry-keepalive/horus_keepalive.py'
    with session.lock():
        session.environment()
        if session.text('rev-parse', 'HEAD') != head or session.status():
            raise ValueError('REVIEWED_CLEAN_HEAD_REQUIRED')
        if session.state.get('validation', {}).get('tree') != session.text('rev-parse', 'HEAD^{tree}'):
            raise ValueError('PROJECT_VALIDATION_REQUIRED')
        status = json.loads(run([str(home / '.local/bin/mestry-bridge'), 'status']))
        if status.get('owned_process_running'):
            raise ValueError('BRIDGE_RUNNING_REVIEW_ACTIVITY_BEFORE_ACTIVATION')
        old = json.loads((base / 'current.json').read_text())
        previous = Path(old['directory'])
        if previous.parent != base / 'releases':
            raise ValueError('INSTALLED_RELEASE_PATH_REQUIRED')
        upgrade.verify_release(previous, old['manifest_sha256'])
        backup = Path(tempfile.mkdtemp(prefix='h3-', dir=base / 'backups'))
        wrapper = home / '.local/bin/mestry-bridge'
        for name, path in [('keeper.py', keeper_source), ('current.json', base / 'current.json'), ('mestry-bridge', wrapper)]:
            if path.is_symlink() or not path.is_file():
                raise ValueError('PRIVATE_INSTALL_FILE_REQUIRED')
            upgrade.atomic_write(backup / name, path.read_bytes(), 0o700 if name.endswith('.py') else 0o600)
        config = home / '.local/state/mestry-keepalive/projects.json'
        if config.exists():
            raise ValueError('EXISTING_PROJECT_POLL_CONFIG_REQUIRES_REVIEW')
        keeper_status = json.loads(run([str(keeper), 'status']))
        with tempfile.TemporaryDirectory(prefix='h3-overlay-', dir=base) as temporary:
            source = Path(temporary) / 'release'
            manifest_sha = compose_release(previous, source, ROOT)
            if keeper_status.get('worker_running'):
                run([str(keeper), 'stop'])
            try:
                upgrade.upgrade(source)
                upgrade.atomic_write(keeper_source, (ROOT / 'tools/s23-remote-access/horus_keepalive.py').read_bytes(), 0o700)
                write_private(config, {'schema': 1, 'projects': [str(ROOT)]})
                run([str(keeper), 'start'])
            except Exception:
                # The project lock excludes all managed new-project turns while
                # installation is in flight. Restore the old code selection if
                # a later worker step failed after the bridge upgrade succeeded.
                if (base / 'current.json').read_bytes() != (backup / 'current.json').read_bytes():
                    run([str(wrapper), 'stop'])
                    upgrade.atomic_write(base / 'current.json', (backup / 'current.json').read_bytes())
                    upgrade.atomic_write(wrapper, (backup / 'mestry-bridge').read_bytes(), 0o700)
                upgrade.atomic_write(keeper_source, (backup / 'keeper.py').read_bytes(), 0o700)
                config.unlink(missing_ok=True)
                if keeper_status.get('worker_running'):
                    run([str(keeper), 'start'])
                raise
        record = {'activated_at': now(), 'project_head': head, 'manifest_sha256': manifest_sha,
                  'previous_release': previous.name, 'rollback_directory': str(backup),
                  'poll_seconds': 120, 'automatic_apply': 'managed_entry_only', 'new_services': False}
        private_dir(home / '.local/state/mestry-h3')
        write_private(home / '.local/state/mestry-h3/deployment.json', record)
        return {'state': 'H3_ADMITTED', 'head': head, 'poll_seconds': 120, 'credentials_changed': False,
                'new_services': False, 'manifest_sha256': manifest_sha}


def receipt():
    expected_profile()
    session = Session(ROOT)
    session.load()
    value = session.state.get('validation', {})
    if value.get('tree') != session.text('rev-parse', 'HEAD^{tree}'):
        raise ValueError('CURRENT_VALIDATION_REQUIRED')
    version = session.environment()
    destination = ROOT / 'docs/validation/H3_S23_RECEIPT.md'
    if destination.exists():
        raise ValueError('RECEIPT_EXISTS_REVIEW_BEFORE_REPLACEMENT')
    destination.write_text('# H3 — S23 checkout receipt\n\n'
        + 'Generated at: ' + now() + '\n\n'
        + '- Source commit: `' + session.text('rev-parse', 'HEAD') + '`\n'
        + '- Target: `' + version['target'] + '`\n'
        + '- Runtime versions: `' + json.dumps(version['versions'], sort_keys=True) + '`\n'
        + '- Candidate validation: `' + json.dumps(value['results'], sort_keys=True) + '`\n'
        + '- Scope: this device executed the repository tests; no conversation export.\n'
        + '- Long-running availability and PC-off validation remain H5.\n')
    return {'receipt': str(destination.relative_to(ROOT)), 'validation': value['results']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['verify', 'activate', 'receipt'])
    parser.add_argument('--head')
    parser.add_argument('--review', action='store_true')
    args = parser.parse_args()
    try:
        if args.operation == 'activate':
            if not args.review or not args.head or not re.fullmatch('[0-9a-f]{40}', args.head):
                raise ValueError('EXPLICIT_REVIEWED_HEAD_REQUIRED')
            result = activate(args.head)
        elif args.operation == 'verify':
            result = verify()
        else:
            result = receipt()
        print(json.dumps(result, sort_keys=True))
    except Exception as error:
        reason = str(error) if isinstance(error, (ValueError, Blocked)) and re.fullmatch('[A-Z_0-9]+', str(error)) else 'H3_ACTION_FAILED_NO_PRIVATE_DETAILS'
        print(json.dumps({'state': 'BLOCKED', 'reason': reason}))
        raise SystemExit(3)

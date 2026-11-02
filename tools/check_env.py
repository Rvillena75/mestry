#!/usr/bin/env python3
"""Read-only capability/fingerprint check. Never installs or copies dependencies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys


def target():
    kind = "wsl" if "microsoft" in platform.release().lower() else platform.system().lower()
    if platform.system() == "Linux" and platform.machine() == "aarch64":
        try:
            if 'ID=alpine' in Path('/etc/os-release').read_text():
                kind = "alpine"
        except OSError:
            pass
    return kind + "-" + platform.machine()


def fingerprint(root, contract):
    values = []
    for name in contract.get("dependency_inputs", []):
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("DEPENDENCY_INPUT_MISSING_OR_SYMLINK")
        values.append([name, hashlib.sha256(path.read_bytes()).hexdigest()])
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


def check(root, contract):
    versions = {"python": platform.python_version()}
    errors = []
    actual_target = target()
    if actual_target not in contract["targets"]:
        errors.append("TARGET_NOT_ADMITTED")
    for name, minimum in contract.get("requirements", {}).items():
        if name != "python":
            executable = shutil.which(name)
            if not executable:
                errors.append("MISSING_" + name.upper())
                continue
            result = subprocess.run([executable, "--version"], capture_output=True, timeout=10)
            match = re.search(rb"\d+\.\d+(?:\.\d+)?", result.stdout)
            if result.returncode or not match:
                errors.append("VERSION_UNKNOWN_" + name.upper())
                continue
            versions[name] = match.group().decode()
        found = tuple(map(int, versions[name].split(".")[:2]))
        if found < tuple(map(int, minimum.split(".")[:2])):
            errors.append("VERSION_TOO_OLD_" + name.upper())
    patch = contract.get("pinned_patch")
    if patch:
        pins = json.loads((root / patch["pins"]).read_text())
        if hashlib.sha256((root / patch["patch"]).read_bytes()).hexdigest() != pins["patch_sha256"]:
            errors.append("PINNED_PATCH_MISMATCH")
    return {"target": actual_target, "versions": versions, "errors": errors,
            "dependency_fingerprint": fingerprint(root, contract),
            "installations_performed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--state-root", type=Path)
    args = parser.parse_args()
    try:
        result = check(args.repo, json.loads((args.repo / ".mestry-workflow.json").read_text()))
        root = args.repo.resolve()
        base = args.state_root or Path.home() / '.local/state/mestry-workflow'
        config = base / hashlib.sha256(os.fsencode(root)).hexdigest()[:20] / 'config.json'
        result['approval_status'] = 'not_configured'
        if config.exists():
            info = config.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise ValueError('PRIVATE_CONFIG_PERMISSIONS')
            approved = json.loads(config.read_text())
            if approved['root'] != str(root):
                raise ValueError('CONFIG_ROOT_MISMATCH')
            changed = approved['dependency_fingerprint'] != result['dependency_fingerprint']
            result['approval_status'] = 'changed_review_required' if changed else 'matches'
            if changed:
                result['errors'].append('DEPENDENCIES_CHANGED_REVIEW_REQUIRED')
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(3 if result["errors"] else 0)
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        print(json.dumps({"errors": ["ENVIRONMENT_CHECK_FAILED"], "installations_performed": False}))
        raise SystemExit(3)

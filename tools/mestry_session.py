#!/usr/bin/env python3
"""Run an explicit SSH/ADB script and retain command, output and timestamps locally.

No private-key/password material is read. SSH uses the existing host alias.
This is an operator's logger, not an unattended installer or cleanup tool.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import pathlib
import subprocess
import time


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--directory', required=True, type=pathlib.Path)
    ap.add_argument('--name', required=True)
    ap.add_argument('--channel', choices=['ssh', 'adb', 'host'], default='ssh')
    ap.add_argument('--script', required=True, type=pathlib.Path)
    ap.add_argument('--timeout', type=int, default=90)
    ap.add_argument('--ssh-debug', action='store_true')
    args = ap.parse_args()
    if not args.name.replace('_', '').isalnum():
        ap.error('name must be letters, digits and underscores')
    out = args.directory
    out.mkdir(parents=True, exist_ok=True)
    target = out / (args.name + '.sh')
    body = args.script.read_text()
    if target.exists():
        raise SystemExit('Probe name already exists; choose a new name to preserve history.')
    target.write_text(body)
    if args.channel == 'ssh':
        argv = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
                '-o', 'ControlMaster=no', '-o', 'ControlPath=none',
                '-o', 'PreferredAuthentications=publickey', '-o', 'PasswordAuthentication=no',
                '-o', 'KbdInteractiveAuthentication=no', '-o', 'IdentityAgent=none']
        if args.ssh_debug:
            argv.append('-vv')
        argv += ['mestry-s23', 'bash -s --']
    elif args.channel == 'adb':
        devices = subprocess.run(['adb.exe', 'devices', '-l'], text=True,
                                 capture_output=True, timeout=20)
        import re
        matches = re.findall(r'^\S+\s+device\s+.*model:SM_S918B\b.*transport_id:(\d+)',devices.stdout,re.M)
        if len(matches) != 1:
            raise SystemExit('Expected exactly one authorized SM-S918B.')
        argv = ['adb.exe', '-t', matches[0], 'shell', 'sh -s']
    else:
        argv = ['bash', '-s', '--']
    record = dict(name=args.name, channel=args.channel, argv=argv,
                  command_file=target.name, started_utc=now(), timeout_seconds=args.timeout)
    print(json.dumps({'started':args.name,'at':record['started_utc']}),flush=True)
    stdout = out / (args.name + '.stdout.txt')
    stderr = out / (args.name + '.stderr.txt')
    with stdout.open('w') as so, stderr.open('w') as se:
        proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=so, stderr=se, text=True)
        try:
            proc.communicate(body, timeout=args.timeout)
            record['returncode'] = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            record['returncode'] = 124
            record['host_timeout'] = True
            record['remote_state'] = 'Unknown whether a remote mutation completed; inspect before retrying.'
    record['ended_utc'] = now()
    record['stdout_file'] = stdout.name
    record['stderr_file'] = stderr.name
    record['files_sha256'] = {f.name:hashlib.sha256(f.read_bytes()).hexdigest()
                              for f in [target, stdout, stderr]}
    (out/(args.name+'.record.json')).write_text(json.dumps(record, indent=2)+'\n')
    with (out/'.manifest.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest_path = out / 'manifest.json'
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
            'started_utc':record['started_utc'], 'device':'SM-S918B; serial not retained',
            'scope':'Authorized SSH recovery/Boot and minimal Debian 13 PRoot installation. No reboot, root, partition changes, debloating, RAM Plus changes or graphics.',
            'probes':[]}
        manifest['probes'].append(record)
        manifest['updated_utc'] = record['ended_utc']
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
        with (out/'commands.md').open('a') as f:
            f.write(f'\n### {args.name}\n\n'
                    f'Canal `{args.channel}`; {record["started_utc"]} → {record["ended_utc"]}; '
                    f'código **{record["returncode"]}**. '
                    f'[Comando]({target.name}), [stdout]({stdout.name}), [stderr]({stderr.name}).\n')
    print(json.dumps(record, indent=2, ensure_ascii=False),flush=True)
    raise SystemExit(record['returncode'])


if __name__ == '__main__':
    main()

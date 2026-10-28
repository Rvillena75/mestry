#!/usr/bin/env python3
"""Read-only readiness check; no login, installs, settings changes or listeners."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess


ADB = '/mnt/c/Users/developer/AppData/Local/Android/Sdk/platform-tools/adb.exe'
DEVICES = {'s23': ('S23_SERIAL', 'SM-S918B'), 's25': ('S25_SERIAL', 'SM-S938B')}
PACKAGES = ('com.termux', 'com.termux.boot', 'com.scariflabs.horus',
            'com.tailscale.ipn', 'org.connectbot', 'com.haochen.codexremote.mestrypilot')


def command(arguments, **kwargs):
    result = subprocess.run(arguments, capture_output=True, text=True, timeout=25, **kwargs)
    if result.returncode:
        # Diagnostics may contain private content. Never echo raw output/errors.
        raise RuntimeError('READ_ONLY_COMMAND_FAILED')
    return result.stdout.strip()


def phone(serial, *args):
    return command([ADB, '-s', serial, 'shell', *args])


def inspect_phone(serial, expected):
    model = phone(serial, 'getprop', 'ro.product.model')
    if model != expected:
        raise RuntimeError('DEVICE_MODEL_MISMATCH')
    installed = set(phone(serial, 'pm', 'list', 'packages').splitlines())
    whitelist = phone(serial, 'cmd', 'deviceidle', 'whitelist').splitlines()
    result = {
        'serial': serial, 'model': model,
        'installed': {p: 'package:' + p in installed for p in PACKAGES},
        'battery_whitelisted': {p: any(',' + p + ',' in line for line in whitelist) for p in PACKAGES},
        'always_on_vpn_app': phone(serial, 'settings', 'get', 'secure', 'always_on_vpn_app'),
        'vpn_lockdown': phone(serial, 'settings', 'get', 'secure', 'always_on_vpn_lockdown'),
    }
    battery = {}
    for line in phone(serial, 'dumpsys', 'battery').splitlines():
        key, separator, value = line.strip().partition(':')
        if separator and key in {'AC powered', 'USB powered', 'Wireless powered', 'level', 'temperature'}:
            battery[key] = value.strip()
    result['battery'] = battery
    if expected == 'SM-S918B':
        raw = phone(serial, 'content', 'call', '--uri', 'content://com.scariflabs.horus.remote', '--method', 'status')
        info = json.JSONDecoder().raw_decode(raw.split('json=', 1)[1])[0]
        result['horus'] = {k: info.get(k) for k in ('status', 'appVersion', 'configured', 'enabled', 'state', 'port', 'keys', 'batteryUnrestricted')}
        services = phone(serial, 'dumpsys', 'activity', 'services', 'com.scariflabs.horus')
        result['horus_foreground_service'] = bool(re.search(r'isForeground=true', services))
        power = phone(serial, 'dumpsys', 'power')
        result['horus_wake_lock_visible'] = bool(re.search(r'WakeLock.*Horus|PARTIAL_WAKE_LOCK.*Horus', power, re.I))
        result['termux_wake_lock_visible'] = bool(re.search(r'WakeLock.*[Tt]ermux|PARTIAL_WAKE_LOCK.*[Tt]ermux', power))
    return result


TERMUX = r'''
import hashlib, json, pathlib, subprocess
home = pathlib.Path.home()
prefix = pathlib.Path('/data/data/com.termux/files/usr')
output = subprocess.run([str(prefix/'bin/sshd'), '-T'], capture_output=True, text=True, timeout=8, check=True).stdout
keys = {'port', 'listenaddress', 'passwordauthentication', 'kbdinteractiveauthentication', 'pubkeyauthentication', 'authenticationmethods', 'allowtcpforwarding', 'gatewayports'}
policy = {}
for line in output.splitlines():
    fields = line.split(None, 1)
    if len(fields) != 2:
        continue
    key, value = fields
    key = key.lower()
    if key in keys:
        policy.setdefault(key, []).append(value)
files = {}
for name in ['.termux/boot/10-mestry-sshd', 'bin/mestry-ssh-start']:
    content = (home/name).read_bytes()
    files[name] = {'sha256': hashlib.sha256(content).hexdigest(), 'has_wake_lock': b'termux-wake-lock' in content}
print(json.dumps({'ssh_policy': policy, 'startup_files': files, 'authorized_keys_sha256': hashlib.sha256((home/'.ssh/authorized_keys').read_bytes()).hexdigest()}))
'''


def collect():
    devices = {name: inspect_phone(*identity) for name, identity in DEVICES.items()}
    termux = json.loads(command(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
                                'mestry-s23', 'python3 -'], input=TERMUX))
    policy = termux['ssh_policy']
    if (policy.get('port') != ['8023'] or policy.get('passwordauthentication') != ['no']
            or policy.get('kbdinteractiveauthentication') != ['no']
            or policy.get('authenticationmethods') != ['publickey']):
        raise RuntimeError('CURRENT_SSH_POLICY_REQUIRES_REVIEW')
    return {'status': 'READ_ONLY_PREFLIGHT_COMPLETE',
            'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'devices': devices, 'termux': termux,
            'phone_settings_changed': False, 'apps_installed': False,
            'new_listeners': False, 'remote_access_validation_performed': False,
            'reboot_tested': False, 'availability_24h_tested': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise RuntimeError('OUTPUT_EXISTS_CHOOSE_NEW_PATH')
        result = collect()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
        print(json.dumps({'status': result['status'], 'output': str(args.output),
                          'remote_access_validation_performed': False, 'new_listeners': False}))
    except Exception as error:
        code = str(error) if type(error) is RuntimeError else 'PREFLIGHT_FAILED_NO_RAW_OUTPUT'
        print(json.dumps({'status': 'ERROR', 'code': code}))
        raise SystemExit(1)

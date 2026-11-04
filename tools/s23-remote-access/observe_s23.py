#!/usr/bin/env python3
"""Bounded, metadata-only observation using an existing ADB server and SSH alias."""
import argparse
import base64
import datetime as dt
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time


class ProbeError(Exception):
    pass


class ExistingAdb:
    def __init__(self, serial, *, powershell=None, host='127.0.0.1', port=5037):
        if not re.fullmatch('[A-Za-z0-9_.:-]+', serial):
            raise ProbeError('INVALID_DEVICE_SELECTOR')
        self.serial, self.powershell, self.host, self.port = serial, powershell, host, port

    def shell(self, command):
        if self.powershell:
            # Commands and replies travel on stdin/stdout. Never launch adb.exe.
            code = r'''
$ErrorActionPreference='Stop'
$q=[Console]::In.ReadToEnd() | ConvertFrom-Json
function Exact($s,[int]$n){$b=New-Object byte[] $n;$p=0;while($p -lt $n){$r=$s.Read($b,$p,$n-$p);if($r -le 0){throw 'EOF'};$p+=$r};return ,$b}
function Request($s,[string]$v){$b=[Text.Encoding]::UTF8.GetBytes($v);$h=[Text.Encoding]::ASCII.GetBytes(('{0:x4}' -f $b.Length));$s.Write($h,0,4);$s.Write($b,0,$b.Length);if([Text.Encoding]::ASCII.GetString((Exact $s 4)) -ne 'OKAY'){throw 'REJECTED'}}
$c=New-Object Net.Sockets.TcpClient
try{$task=$c.ConnectAsync($q.host,[int]$q.port);if(-not $task.Wait(5000)){throw 'CONNECT'};$s=$c.GetStream();$s.ReadTimeout=20000;Request $s ('host:transport:'+$q.serial);Request $s ('shell:'+$q.command);$m=New-Object IO.MemoryStream;$b=New-Object byte[] 8192;while(($n=$s.Read($b,0,$b.Length)) -gt 0){$m.Write($b,0,$n);if($m.Length -gt 2097152){throw 'LIMIT'}};[Convert]::ToBase64String($m.ToArray())}finally{$c.Dispose()}
'''
            result = subprocess.run([self.powershell, '-NoProfile', '-NonInteractive',
                '-EncodedCommand', base64.b64encode(code.encode('utf-16le')).decode()],
                input=json.dumps(dict(serial=self.serial, host=self.host, port=self.port,
                                     command=command)), capture_output=True, text=True,
                encoding='utf-8', errors='replace', timeout=30)
            if result.returncode:
                raise ProbeError('EXISTING_ADB_QUERY_FAILED')
            try:
                return base64.b64decode(result.stdout.strip(), validate=True).decode('utf-8').replace('\r', '')
            except (ValueError, UnicodeError):
                raise ProbeError('INVALID_ADB_RESPONSE') from None
        try:
            with socket.create_connection((self.host, self.port), timeout=20) as connection:
                def exact(length):
                    data = b''
                    while len(data) < length:
                        part = connection.recv(length-len(data))
                        if not part:
                            raise ProbeError('INCOMPLETE_ADB_RESPONSE')
                        data += part
                    return data
                for request in ['host:transport:'+self.serial, 'shell:'+command]:
                    payload = request.encode()
                    connection.sendall(('%04x' % len(payload)).encode()+payload)
                    if exact(4) != b'OKAY':
                        raise ProbeError('EXISTING_ADB_QUERY_REJECTED')
                data = b''
                while part := connection.recv(65536):
                    data += part
                    if len(data) > 2_097_152:
                        raise ProbeError('ADB_RESPONSE_LIMIT')
                return data.decode('utf-8').replace('\r', '')
        except OSError:
            raise ProbeError('EXISTING_ADB_UNAVAILABLE') from None


def metadata(raw):
    result = {}
    for name, value in re.findall(r'^\s*(USB powered|AC powered|level|temperature):\s*(\S+)', raw, re.M):
        if name in ('USB powered', 'AC powered') and value in ('true', 'false'):
            result[name] = value == 'true'
        elif name in ('level', 'temperature') and re.fullmatch(r'-?\d+', value):
            result[name] = int(value)
    for name, pattern in [('mem_available_kib', r'^MemAvailable:\s*(\d+)'),
                          ('thermal_status', r'^Thermal Status:\s*(\d+)')]:
        match = re.search(pattern, raw, re.M)
        if match:
            result[name] = int(match[1])
    match = re.search(r'mWakefulness=(Awake|Asleep|Dozing|Dreaming)\b', raw)
    if match:
        result['wakefulness'] = match[1]
    return result


def sample(adb, ssh_host, expected_model='SM-S918B'):
    if adb.shell('getprop ro.product.model').strip() != expected_model:
        raise ProbeError('DEVICE_MODEL_MISMATCH')
    raw = adb.shell('dumpsys battery; cat /proc/meminfo; dumpsys power; dumpsys thermalservice')
    value = metadata(raw)
    if not {'level', 'temperature', 'mem_available_kib', 'wakefulness'}.issubset(value):
        raise ProbeError('REQUIRED_ANDROID_METADATA_MISSING')
    # Health contains no credentials. SSH uses the existing alias and host pin.
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
        '-o', 'StrictHostKeyChecking=yes', ssh_host,
        'curl --max-time 5 -fsS http://127.0.0.1:8787/healthz'],
        capture_output=True, text=True, timeout=20)
    try:
        health = json.loads(result.stdout)
        value['bridge_health'] = result.returncode == 0 and health.get('ok') is True and \
            health.get('name') == 'mestry-s25-pilot' and health.get('version') == '0.1.0'
    except (ValueError, AttributeError):
        value['bridge_health'] = False
    return value


def summary(samples, complete):
    valid = [row for row in samples if 'error' not in row]
    idle = [row for row in valid if row.get('wakefulness') in ('Dozing', 'Asleep')]
    return dict(complete=complete, samples=len(samples), successful_samples=len(valid),
                health_passes=sum(row.get('bridge_health') is True for row in valid),
                idle_samples=len(idle), all_samples_healthy=bool(valid) and len(valid)==len(samples)
                and all(row.get('bridge_health') is True for row in valid),
                availability_24h_verified=False, pc_off_verified=False,
                reboot_recovery_verified=False)


def save(path, value):
    fd, temporary = tempfile.mkstemp(prefix='.observation-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--powershell')
    parser.add_argument('--ssh-host', default='mestry-s23')
    parser.add_argument('--duration', type=int, default=1200)
    parser.add_argument('--interval', type=int, default=30)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 60 <= args.duration <= 1800 or not 15 <= args.interval <= 60:
        parser.error('duration 60..1800 seconds; interval 15..60 seconds')
    if args.ssh_host.startswith('-') or not re.fullmatch('[A-Za-z0-9_.-]+', args.ssh_host):
        parser.error('use an existing SSH host alias')
    output = args.output.absolute()
    if output.exists() or output.is_symlink() or not output.parent.is_dir():
        parser.error('output must be a new file in an existing private directory')
    parent = output.parent
    if parent.is_symlink() or parent.stat().st_mode & 0o077 or parent.stat().st_uid != os.getuid():
        parser.error('output directory must belong to this user and have mode 700')
    os.umask(0o077)
    adb = ExistingAdb(args.serial, powershell=args.powershell)
    rows = []
    started = time.monotonic()
    complete = False
    try:
        while True:
            elapsed = time.monotonic()-started
            row = dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(), elapsed_s=round(elapsed, 2))
            try:
                row.update(sample(adb, args.ssh_host))
            except (ProbeError, OSError, subprocess.TimeoutExpired) as error:
                row['error'] = str(error) if isinstance(error, ProbeError) else 'QUERY_FAILED_NO_PRIVATE_DETAILS'
            rows.append(row)
            complete = elapsed >= args.duration
            value = dict(marker='MESTRY_S23_OBSERVATION', duration_requested_s=args.duration,
                         observer='host queries; may wake CPU; no forced idle or screen actions',
                         samples=rows, summary=summary(rows, complete))
            save(output, value)
            print(json.dumps(dict(sample=len(rows), **row)), flush=True)
            if complete:
                break
            deadline = started + min(len(rows)*args.interval, args.duration)
            time.sleep(max(0, deadline-time.monotonic()))
    except KeyboardInterrupt:
        print(json.dumps(summary(rows, False)), flush=True)
        return 130
    print(json.dumps(summary(rows, complete)), flush=True)
    return 0 if value['summary']['all_samples_healthy'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

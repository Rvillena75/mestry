#!/usr/bin/env python3
"""Bounded cellular check; restore Wi-Fi and temporary metadata logging in finally."""
import argparse
import datetime
import json
from pathlib import Path
import re
import shlex
import sys
import time

from device_ui import adb, dump
from network_test import APP, CACHE, cellular_ready, mobile_metadata, shell
from preflight import DEVICES
from reconnect_private_ui import reconnect, ui


def wifi_setting(enabled):
    ui('launch-wifi-settings')
    nodes = dump(DEVICES['s25'][0])
    switches = [n for n in nodes if n.get('resource-id') == 'com.android.settings:id/sesl_switchbar_switch']
    if len(switches) != 1:
        raise RuntimeError('UNIQUE_SYSTEM_WIFI_SWITCH_REQUIRED')
    switch = switches[0]
    if (switch.get('checked') == 'true') != enabled:
        ui('tap-bounds', switch.get('bounds'))
    ui('launch-app', APP)


def history_metadata(since, until=float('inf')):
    raw = shell('logcat', '-d', '-v', 'epoch', '--uid=10551', '-s', 'CodexRemoteSync:D', '*:S')
    rows = []
    pattern = re.compile(r'^\s*(\d+\.\d+).*?CodexRemoteSync\s*:\s*'
                         r'session\.content response sessionId=([a-zA-Z0-9-]+) '
                         r'last=(-?\d+) entries=(\d+) items=(\d+) conversationBefore=(\d+)\s*$')
    sync_pattern = re.compile(r'^\s*(\d+\.\d+).*?CodexRemoteSync\s*:\s*'
                              r'session\.sync applied sessionId=([a-zA-Z0-9-]+) '
                              r'conversationItems=(\d+) cacheEntries=(\d+)\s*$')
    for line in raw.splitlines():
        match = pattern.match(line)
        if match and since <= float(match[1]) <= until:
            rows.append({'device_epoch': float(match[1]), 'session_id': match[2],
                         'method': 'session.content',
                         'last_seq': int(match[3]), 'entries': int(match[4]),
                         'items': int(match[5]), 'conversation_items_before': int(match[6])})
        match = sync_pattern.match(line)
        if match and since <= float(match[1]) <= until:
            rows.append({'device_epoch': float(match[1]), 'session_id': match[2],
                         'method': 'session.sync', 'entries': int(match[4]), 'items': int(match[3]),
                         'entries_are_merged_history_count': True,
                         'freshness_evidence': 'Applied inside the successful server response callback, not cache load.'})
    return rows


def validate(output):
    if output.exists():
        raise RuntimeError('OUTPUT_EXISTS')
    serial, expected = DEVICES['s25']
    if shell('getprop', 'ro.product.model') != expected:
        raise RuntimeError('S25_MODEL_REQUIRED')
    initial = mobile_metadata()
    if not initial['wifi_enabled'] or not initial['mobile_data_enabled']:
        raise RuntimeError('EXISTING_WIFI_AND_MOBILE_DATA_REQUIRED')
    if shell('settings', 'get', 'global', 'airplane_mode_on') != '0':
        raise RuntimeError('AIRPLANE_MODE_MUST_ALREADY_BE_OFF')
    roaming = shell('getprop', 'gsm.operator.isroaming')
    if not roaming or any(part.strip() != 'false' for part in roaming.split(',')):
        raise RuntimeError('CONFIRMED_NON_ROAMING_REQUIRED')
    previous_tag = shell('getprop', 'log.tag.CodexRemoteSync')
    started = time.monotonic()
    result = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'serial': serial, 'model': expected, 'initial_network': initial,
              'roaming_confirmed_false': True, 'model_turns_started': 0,
              'files_published': 0, 'credentials_read_or_copied': False}
    try:
        # Existing tag logs IDs/counts, not message text. Never save raw logcat.
        shell('setprop', 'log.tag.CodexRemoteSync', 'DEBUG')
        wifi_setting(False)
        for _ in range(20):
            before = mobile_metadata()
            if cellular_ready(before):
                break
            time.sleep(.5)
        else:
            raise RuntimeError('CELLULAR_DEFAULT_WITHOUT_WIFI_REQUIRED')
        result['network_before_new_ssh'] = before
        result['wifi_disabled_through_android_settings_ui'] = True
        since = float(shell('date', '+%s'))
        result['history_window_start_device_epoch'] = since
        print(json.dumps({'stage': 'cellular_route_verified', 'network': before}), flush=True)
        result['new_private_ssh_and_hello'] = reconnect()
        print(json.dumps({'stage': 'new_ssh_and_hello', 'status': result['new_private_ssh_and_hello']['status']}), flush=True)
        result['network_after_new_ssh'] = mobile_metadata()
        if not cellular_ready(result['network_after_new_ssh']):
            raise RuntimeError('CELLULAR_ROUTE_CHANGED_DURING_SSH')
        for entry, main in [('tcp_ssh_banner', 'RemoteNetworkProbe'), ('loopback_tunnel', 'LoopbackProbe')]:
            raw = shell('run-as', APP, 'env', 'CLASSPATH=' + CACHE,
                        'app_process', '/system/bin', main)
            result[entry] = json.loads(raw)
        for _ in range(6):
            rows = history_metadata(since)
            if any(row['entries'] > 0 and row['items'] > 0 for row in rows):
                break
            time.sleep(1)
        result['fresh_history_responses'] = rows
        result['network_after_all_probes'] = mobile_metadata()
        result['history_window_end_device_epoch'] = float(shell('date', '+%s'))
        result['cellular_route_verified_before_and_after'] = all(cellular_ready(result[name]) for name in
            ['network_before_new_ssh', 'network_after_new_ssh', 'network_after_all_probes'])
        result['fresh_history_status'] = 'PASS' if any(row['entries'] > 0 and row['items'] > 0 for row in rows) else 'NOT_CONFIRMED'
        passed = (result['cellular_route_verified_before_and_after']
                  and result['new_private_ssh_and_hello']['status'] == 'PASS'
                  and result['tcp_ssh_banner'].get('status') == 'PASS'
                  and result['loopback_tunnel'].get('status') == 'PASS'
                  and result['fresh_history_status'] == 'PASS')
        result['status'] = 'PASS' if passed else 'PARTIAL'
    except Exception as error:
        result['status'] = 'INCONCLUSIVE'
        result['error'] = str(error) if type(error) is RuntimeError and re.fullmatch('[A-Z0-9_]+', str(error)) else 'VALIDATION_FAILED_NO_RAW_OUTPUT'
    finally:
        try:
            try:
                wifi_setting(True)
            except Exception:
                shell('svc', 'wifi', 'enable')
        finally:
            shell('setprop', 'log.tag.CodexRemoteSync', shlex.quote(previous_tag))
        for _ in range(12):
            restored = mobile_metadata()
            default = restored.get('active_default_transport') or {}
            if restored['wifi_enabled'] and default.get('transports') == 'WIFI' and default.get('validated'):
                break
            time.sleep(.5)
        result['network_restored'] = restored
        result['wifi_restored'] = restored['wifi_enabled']
        result['temporary_log_tag_restored'] = shell('getprop', 'log.tag.CodexRemoteSync') == previous_tag
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.output)
    raise SystemExit(0 if result['status'] == 'PASS' else 1)

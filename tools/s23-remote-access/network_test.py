#!/usr/bin/env python3
"""Run reviewed no-secret probes as MESTRY UID, optionally over temporary mobile data."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from preflight import ADB, DEVICES

APP = 'com.haochen.codexremote.mestrypilot'
DEX = Path('/mnt/c/Users/developer/AppData/Local/mestry-build/remote-network-20261022T034500Z/dex/classes.dex')
WINDOWS_DEX = r'C:\Users\developer\AppData\Local\mestry-build\remote-network-20261022T034500Z\dex\classes.dex'
CACHE = '/data/user/0/' + APP + '/cache/mestry-remote-network.dex'


def adb(*args):
    serial, _ = DEVICES['s25']
    result = subprocess.run([ADB, '-s', serial, *args], capture_output=True, text=True, timeout=35)
    if result.returncode:
        raise RuntimeError('DIAGNOSTIC_COMMAND_FAILED_NO_RAW_OUTPUT')
    return result.stdout.strip()


def shell(*args):
    return adb('shell', *args)


def mobile_metadata():
    connectivity = shell('dumpsys', 'connectivity')
    transports = []
    default_match = re.search(r'Active default network:\s*(\d+)', connectivity)
    default_id = default_match.group(1) if default_match else None
    default_transport = None
    # Select capabilities on agent header lines; omit addresses, SSIDs and subscriptions.
    for line in connectivity.splitlines():
        if not line.lstrip().startswith('NetworkAgentInfo{'):
            continue
        match = re.search(r'Transports:\s*([A-Z|_ ]+?)\s+Capabilities:', line)
        if match:
            network = re.search(r'network\{(\d+)\}', line)
            item = {'transports': match.group(1).strip(), 'validated': 'VALIDATED' in line,
                    'connected': bool(re.search(r'\bCONNECTED\b', line))}
            transports.append(item)
            if network and network.group(1) == default_id:
                default_transport = item
    return {'wifi_enabled': 'Wifi is enabled' in shell('cmd', 'wifi', 'status'),
            'mobile_data_enabled': shell('settings', 'get', 'global', 'mobile_data') == '1',
            'active_default_transport': default_transport, 'transport_capabilities': transports}


def cellular_ready(metadata):
    current = metadata.get('active_default_transport') or {}
    transport = set(current.get('transports', '').split('|'))
    wifi_agents = [item for item in metadata.get('transport_capabilities', [])
                   if 'WIFI' in item.get('transports', '').split('|')]
    return (not metadata['wifi_enabled'] and 'CELLULAR' in transport
            and 'WIFI' not in transport and current.get('validated', False) and not wifi_agents)


def execute(args):
    if args.output.exists():
        raise RuntimeError('OUTPUT_EXISTS')
    if shell('getprop', 'ro.product.model') != DEVICES['s25'][1]:
        raise RuntimeError('S25_MODEL_REQUIRED')
    if args.mobile:
        if shell('settings', 'get', 'global', 'airplane_mode_on') != '0':
            raise RuntimeError('MOBILE_TEST_REQUIRES_AIRPLANE_MODE_OFF')
        if shell('settings', 'get', 'global', 'mobile_data') != '1':
            raise RuntimeError('MOBILE_DATA_ALREADY_ENABLED_REQUIRED')
        if 'true' in shell('getprop', 'gsm.operator.isroaming'):
            raise RuntimeError('NO_ROAMING_TEST_ALLOWED')
    adb('push', WINDOWS_DEX, '/data/local/tmp/mestry-remote-network.dex')
    shell('run-as', APP, 'rm', '-f', 'cache/mestry-remote-network.dex')
    shell('run-as', APP, 'cp', '/data/local/tmp/mestry-remote-network.dex', 'cache/mestry-remote-network.dex')
    shell('run-as', APP, 'chmod', '444', 'cache/mestry-remote-network.dex')
    wifi_before = 'Wifi is enabled' in shell('cmd', 'wifi', 'status')
    if args.mobile and not wifi_before:
        raise RuntimeError('WIFI_ORIGINAL_STATE_REQUIRED')
    result = None
    try:
        if args.mobile:
            shell('svc', 'wifi', 'disable')
            for _ in range(12):
                metadata = mobile_metadata()
                if cellular_ready(metadata):
                    break
                time.sleep(1)
            else:
                raise RuntimeError('VALIDATED_CELLULAR_NETWORK_REQUIRED')
            time.sleep(2)
            metadata = mobile_metadata()
            if not cellular_ready(metadata):
                print(json.dumps({'marker': 'MESTRY_SAFE_MOBILE_METADATA', 'network': metadata}))
                raise RuntimeError('STABLE_CELLULAR_NETWORK_REQUIRED')
        else:
            metadata = mobile_metadata()
        raw = shell('run-as', APP, 'env', 'CLASSPATH=' + CACHE,
                    'app_process', '/system/bin', 'LoopbackProbe' if args.loopback else 'RemoteNetworkProbe')
        result = json.loads(raw)
        result['checked_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result['probe_dex_sha256'] = hashlib.sha256(DEX.read_bytes()).hexdigest()
        result['network'] = metadata
        result['network_after_probe_before_wifi_restore'] = mobile_metadata()
        result['mobile_test'] = args.mobile
        if args.mobile:
            verified = cellular_ready(metadata) and cellular_ready(result['network_after_probe_before_wifi_restore'])
            result['cellular_route_verified_before_and_after'] = verified
            if not verified:
                result['probe_status'] = result.get('status')
                result['status'] = 'INCONCLUSIVE_CELLULAR_ROUTE'
        result['full_app_ssh_authentication_verified'] = False
    finally:
        if args.mobile:
            shell('svc', 'wifi', 'enable')
    if result is not None:
        result['wifi_restored_if_changed'] = not args.mobile or 'Wifi is enabled' in shell('cmd', 'wifi', 'status')
        args.output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mobile', action='store_true')
    parser.add_argument('--loopback', action='store_true')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        execute(args)
    except Exception as error:
        code = str(error) if type(error) is RuntimeError else 'DIAGNOSTIC_FAILED_NO_RAW_OUTPUT'
        print(json.dumps({'status': 'ERROR', 'code': code}))
        raise SystemExit(1)

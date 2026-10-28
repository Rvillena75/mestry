#!/usr/bin/env python3
"""Read selected VPN lifecycle metadata; never read the bridge vault or chats."""
import argparse
import datetime
import json
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET

from device_ui import adb
from network_test import mobile_metadata
from preflight import DEVICES

APP = 'com.haochen.codexremote.mestrypilot'


def vpn_agents(connectivity):
    result = []
    for line in connectivity.splitlines():
        if not line.lstrip().startswith('NetworkAgentInfo{'):
            continue
        match = re.search(r'Transports:\s*([A-Z|_ ]+?)\s+Capabilities:', line)
        # Physical agents have NOT_VPN capability; it is not a VPN transport.
        if match and 'VPN' in match.group(1).strip().split('|'):
            result.append(line)
    return result


def lifecycle_sample():
    serial, expected = DEVICES['s25']
    start = time.monotonic()
    raw = adb(serial, 'shell', 'getprop ro.product.model; run-as ' + APP
              + ' cat shared_prefs/mestry_vpn_private.xml; dumpsys connectivity')
    model, _, remainder = raw.partition('\n')
    if model.strip() != expected:
        raise RuntimeError('S25_MODEL_REQUIRED')
    xml, delimiter, connectivity = remainder.partition('</map>')
    if not delimiter:
        raise RuntimeError('LIFECYCLE_METADATA_REQUIRED')
    values = {n.get('name'): n.get('value', n.text or '') for n in ET.fromstring(xml + delimiter)}
    return {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sample_duration_seconds': round(time.monotonic() - start, 3),
        'vpn_service_running': values.get('running') == 'true',
        'status': values.get('status'),
        'previous_or_current_stop_reason': values.get('last_stop_reason'),
        'active_task_count': sum(len(ids) for ids in json.loads(values.get('tasks', '{}')).values()),
        'android_vpn_present': bool(vpn_agents(connectivity)),
    }


def snapshot():
    serial, expected = DEVICES['s25']
    model = adb(serial, 'shell', 'getprop', 'ro.product.model').strip()
    if model != expected:
        raise RuntimeError('S25_MODEL_REQUIRED')
    # This separate file contains lifecycle flags and task IDs, never credentials.
    raw = adb(serial, 'shell', 'run-as', APP, 'cat', 'shared_prefs/mestry_vpn_private.xml')
    values = {n.get('name'): n.get('value', n.text or '') for n in ET.fromstring(raw)}
    tasks = json.loads(values.get('tasks', '{}'))
    connectivity = adb(serial, 'shell', 'dumpsys', 'connectivity')
    agents = vpn_agents(connectivity)
    ranges = [m.group(1) for line in agents
              if (m := re.search(r'Uids: <([^>]*)>', line))]
    services = adb(serial, 'shell', 'dumpsys', 'activity', 'services', APP)
    return {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'serial': serial, 'model': model,
        'vpn_service_running': values.get('running') == 'true',
        'vpn_owned': values.get('owned') == 'true',
        'status': values.get('status'),
        'previous_or_current_stop_reason': values.get('last_stop_reason'),
        'active_task_count': sum(len(ids) for ids in tasks.values()),
        'android_mestry_service_present': 'MestryVpnService' in services,
        'android_vpn_present': bool(agents), 'vpn_uid_ranges': ranges,
        'always_on_vpn_app': adb(serial, 'shell', 'settings', 'get', 'secure', 'always_on_vpn_app').strip(),
        'vpn_lockdown': adb(serial, 'shell', 'settings', 'get', 'secure', 'always_on_vpn_lockdown').strip(),
        'network': mobile_metadata(),
        'credentials_read_or_copied': False, 'model_turns_started': 0,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise SystemExit('OUTPUT_EXISTS')
    result = snapshot()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

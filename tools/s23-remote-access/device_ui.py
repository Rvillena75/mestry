#!/usr/bin/env python3
"""USB UI helper for the two known phones; never captures password entry."""
import argparse
from pathlib import Path
import re
import shlex
import subprocess
import xml.etree.ElementTree as ET

from preflight import ADB, DEVICES


def adb(serial, *args):
    return subprocess.check_output([ADB, '-s', serial, *args], text=True, timeout=25)


def dump(serial, public_connection_control=None):
    report = adb(serial, 'shell', 'uiautomator', 'dump', '--compressed', '/data/local/tmp/mestry-remote-ui.xml')
    if 'UI hierchary dumped' not in report and 'UI hierarchy dumped' not in report:
        raise RuntimeError('CURRENT_UI_DUMP_REQUIRED')
    try:
        raw = adb(serial, 'shell', 'cat', '/data/local/tmp/mestry-remote-ui.xml')
    finally:
        adb(serial, 'shell', 'rm', '-f', '/data/local/tmp/mestry-remote-ui.xml')
    nodes = list(ET.fromstring(raw).iter('node'))
    if any(n.get('password') == 'true' for n in nodes):
        # Connection page has a masked key. Locate only the named public button;
        # never return input fields, screen text, or pixels from that page.
        if public_connection_control in {'Conectar', 'Desconectar'}:
            return [n for n in nodes if n.get('package') == 'com.haochen.codexremote.mestrypilot'
                    and n.get('text') == public_connection_control and n.get('password') != 'true']
        raise RuntimeError('PRIVATE_INPUT_SCREEN_DO_NOT_CAPTURE')
    return nodes


def safe(value):
    value = re.sub(r'[^\s@]+@[^\s@]+\.[^\s@]+', '[account]', value)
    return re.sub(r'(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{43,128}(?![A-Za-z0-9_-])', '[opaque value]', value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('device', choices=DEVICES)
    parser.add_argument('action', choices=['inspect', 'tap-text', 'tap-desc', 'tap-bounds', 'tap-connection', 'check-app', 'scroll-to', 'key', 'type-public', 'launch-app', 'launch-wifi-settings', 'launch-tailscale-store', 'capture'])
    parser.add_argument('value', nargs='?')
    args = parser.parse_args()
    serial, model = DEVICES[args.device]
    if adb(serial, 'shell', 'getprop', 'ro.product.model').strip() != model:
        raise RuntimeError('PHONE_MODEL_REQUIRED')
    if args.action == 'launch-wifi-settings':
        adb(serial, 'shell', 'am', 'start', '-a', 'android.settings.WIFI_SETTINGS')
        print('WIFI_SETTINGS_OPENED')
        return
    if args.action == 'launch-app':
        allowed = {'s25': {'org.connectbot', 'com.haochen.codexremote.mestrypilot', 'com.tailscale.ipn'},
                   's23': {'com.termux', 'com.scariflabs.horus', 'com.tailscale.ipn'}}
        if args.value not in allowed[args.device]:
            raise RuntimeError('ONLY_APPROVED_PACKAGES_ALLOWED')
        resolved = adb(serial, 'shell', 'cmd', 'package', 'resolve-activity', '--brief',
                       '-a', 'android.intent.action.MAIN', '-c', 'android.intent.category.LAUNCHER', args.value)
        components = [line.strip() for line in resolved.splitlines()
                      if line.strip().startswith(args.value + '/')]
        if len(components) != 1:
            raise RuntimeError('UNIQUE_LAUNCHER_REQUIRED')
        adb(serial, 'shell', 'am', 'start', '-n', components[0])
        print('APP_LAUNCHER_OPENED')
        return
    if args.action == 'launch-tailscale-store':
        adb(serial, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', 'market://details?id=com.tailscale.ipn', '-p', 'com.android.vending')
        print('OFFICIAL_PLAY_STORE_OPENED')
        return
    if args.action == 'key':
        adb(serial, 'shell', 'input', 'keyevent', str(int(args.value)))
        return
    if args.action == 'tap-connection' and args.value not in {'Conectar', 'Desconectar'}:
        raise RuntimeError('PUBLIC_CONNECTION_BUTTON_REQUIRED')
    nodes = dump(serial, args.value if args.action == 'tap-connection' else None)
    if args.action == 'type-public':
        # For reviewed commands/hosts only. Never use for passwords or tokens.
        if not args.value or not args.value.isascii() or any(ord(c) < 32 for c in args.value):
            raise RuntimeError('SINGLE_LINE_PUBLIC_ASCII_REQUIRED')
        adb(serial, 'shell', 'input', 'text', shlex.quote(args.value.replace(' ', '%s')))
        print('PUBLIC_TEXT_ENTERED')
        return
    if args.action == 'check-app':
        if args.value not in {'org.connectbot', 'com.haochen.codexremote.mestrypilot'}:
            raise RuntimeError('ONLY_APPROVED_PACKAGES_ALLOWED')
        target = next(n for n in nodes if n.get('text') == args.value)
        row = next(n for n in reversed(nodes) if target in list(n.iter()) and any(c.get('checkable') == 'true' for c in n.iter()))
        boxes = [c for c in row.iter() if c.get('checkable') == 'true']
        if len(boxes) != 1:
            raise RuntimeError('UNIQUE_APP_CHECKBOX_REQUIRED')
        box = boxes[0]
        if box.get('checked') == 'true':
            print('APP_ALREADY_INCLUDED')
            return
        x1,y1,x2,y2=map(int,re.findall(r'\d+',box.get('bounds')))
        adb(serial,'shell','input','tap',str((x1+x2)//2),str((y1+y2)//2))
        print('APP_CHECKBOX_SELECTED')
        return
    if args.action == 'scroll-to':
        for attempt in range(7):
            if any(n.get('text') == args.value for n in nodes):
                print('REQUESTED_ITEM_VISIBLE')
                return
            scroll = next((n for n in nodes if n.get('scrollable') == 'true'), None)
            if scroll is None:
                raise RuntimeError('VISIBLE_SCROLL_CONTAINER_REQUIRED')
            x1, y1, x2, y2 = map(int, re.findall(r'\d+', scroll.get('bounds')))
            adb(serial, 'shell', 'input', 'swipe', str((x1+x2)//2), str(y2-150), str(y1+150), '160')
            nodes = dump(serial)
        print('ITEM_NOT_YET_VISIBLE_CONTINUE_SCROLL')
        return
    if args.action == 'inspect':
        for n in nodes:
            text = n.get('text') or n.get('content-desc')
            if text:
                print(safe(text)[:150], n.get('bounds'))
        return
    if args.action.startswith('tap-'):
        attr = {'tap-text': 'text', 'tap-desc': 'content-desc', 'tap-bounds': 'bounds', 'tap-connection': 'text'}[args.action]
        matches = list({n.get('bounds'): n for n in nodes if n.get(attr) == args.value and n.get('enabled') == 'true'}.values())
        if len(matches) != 1:
            raise RuntimeError('EXACT_VISIBLE_UNIQUE_CONTROL_REQUIRED')
        box = list(map(int, re.findall(r'\d+', matches[0].get('bounds', ''))))
        x1, y1, x2, y2 = box
        adb(serial, 'shell', 'input', 'tap', str((x1 + x2) // 2), str((y1 + y2) // 2))
        print('OBSERVED_CONTROL_TAPPED')
        return
    destination = Path(args.value)
    if destination.exists():
        raise RuntimeError('OUTPUT_EXISTS')
    # Pull complete PNG bytes; exec-out from older Windows ADB clients truncated them.
    remote = '/data/local/tmp/mestry-remote-ui.png'
    stage = Path('/mnt/c/Users/developer/AppData/Local/mestry-build') / ('remote-' + args.device + '.png')
    win = str(stage).removeprefix('/mnt/c/').replace('/', '\\')
    adb(serial, 'shell', 'screencap', '-p', remote)
    adb(serial, 'pull', remote, 'C:\\' + win)
    data = stage.read_bytes()
    if not data.endswith(b'\x00\x00\x00\x00IEND\xaeB`\x82'):
        raise RuntimeError('COMPLETE_PNG_REQUIRED')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    stage.unlink()
    print('SCREENSHOT_SAVED')


if __name__ == '__main__':
    main()

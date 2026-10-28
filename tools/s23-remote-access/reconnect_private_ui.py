#!/usr/bin/env python3
"""Reopen the existing S25 Termux profile and await MESTRY's real hello state."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import re
import sys
import time

import device_ui
from preflight import DEVICES
from vpn_observe import lifecycle_sample


def ui(*args):
    previous = sys.argv
    try:
        sys.argv = ['device_ui.py', 's25', *args]
        with contextlib.redirect_stdout(io.StringIO()):
            device_ui.main()
    finally:
        sys.argv = previous


def reconnect():
    serial, expected = DEVICES['s25']
    if device_ui.adb(serial, 'shell', 'getprop', 'ro.product.model').strip() != expected:
        raise RuntimeError('S25_MODEL_REQUIRED')
    if lifecycle_sample()['active_task_count']:
        raise RuntimeError('ACTIVE_TASK_REQUIRES_PRESERVING_SSH')
    ui('launch-app', 'org.connectbot')
    for _ in range(8):
        texts = {n.get('text', '') for n in device_ui.dump(serial)}
        if 'ConnectBot' in texts and 'Mestry s23 8023' in texts:
            break
        if any(t.startswith('¿Estás seguro') and 'Mestry s23 8023' in t for t in texts):
            ui('tap-text', 'Sí')
        elif 'Cerrar' in texts:
            ui('tap-text', 'Cerrar')
        elif 'Desconectar' in texts:
            ui('tap-text', 'Desconectar')
        elif 'Reenvíos de puertos' in texts:
            ui('tap-desc', 'Navegar hacia arriba')
        elif 'Mestry s23 8023' in texts:
            ui('tap-desc', 'Más opciones')
        else:
            ui('key', '4')
    else:
        raise RuntimeError('EXISTING_HOST_LIST_REQUIRED')
    ui('launch-app', 'com.haochen.codexremote.mestrypilot')
    time.sleep(1)
    ui('launch-app', 'org.connectbot')
    ui('tap-text', 'Mestry s23 8023')
    time.sleep(1)
    ui('type-public', 'whoami; printenv SSH_CONNECTION')
    ui('key', '66')
    nodes = device_ui.dump(serial)
    lines = [line.strip() for n in nodes for line in n.get('text', '').splitlines()]
    proof = {'termux_user_matches': 'u0_a348' in lines,
             'ssh_connections': [line for line in lines if re.fullmatch(
                 r'100\.113\.143\.35 \d+ 100\.116\.132\.30 8023', line)]}
    ui('launch-app', 'com.haochen.codexremote.mestrypilot')
    for attempt in range(15):
        state = lifecycle_sample()
        if state['status'] == 'Conexión de MESTRY activa':
            break
        if attempt == 3:
            try:
                ui('tap-connection', 'Conectar')
            except RuntimeError as error:
                if str(error) != 'EXACT_VISIBLE_UNIQUE_CONTROL_REQUIRED':
                    raise
        time.sleep(1)
    return {'serial': serial, 'model': expected, 'ssh': proof, 'hello_service_state': state,
            'status': 'PASS' if proof['termux_user_matches'] and proof['ssh_connections']
            and state['status'] == 'Conexión de MESTRY activa' else 'FAIL',
            'hello_evidence': 'Installed active status is gated by protocol hello handling.',
            'model_turns_started': 0, 'credentials_read_or_copied': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('OUTPUT_EXISTS')
    result = reconnect()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)

#!/usr/bin/env python3
"""Pair the existing S25 public key with Horus through its official ADB provider.

Run interactively in WSL. --check only reads the current state. The password is
read from the local terminal and sent through stdin, never WSL command arguments
or evidence files. Android's content provider receives its required transient
base64 argument; base64 is not encryption. No private SSH key is loaded here.
"""
import argparse
import base64
import datetime as dt
import getpass
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys


S25_FP = 'SHA256:CONFIGURE_LOCAL_FINGERPRINT'
URI = 'content://com.scariflabs.horus.remote'
PAIR_COMMAND = (
    'set +x; IFS= read -r mestry_pair_request || exit 2; '
    'content call --uri ' + URI + ' --method pair --arg "$mestry_pair_request"; '
    'unset mestry_pair_request'
)
SAFE_FIELDS = {
    'status', 'protocol', 'appVersion', 'configured', 'username', 'enabled',
    'state', 'port', 'keys', 'authorized', 'started', 'fingerprint', 'retryAfterMs',
}
SSH = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
       '-o', 'ControlMaster=no', '-o', 'ControlPath=none',
       '-o', 'StrictHostKeyChecking=yes', '-o', 'IdentityAgent=none',
       '-o', 'IdentitiesOnly=yes', '-o', 'PreferredAuthentications=publickey',
       '-o', 'PasswordAuthentication=no', '-o', 'KbdInteractiveAuthentication=no']


class PairError(Exception):
    """An error whose text is safe to display and record."""


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def invoke(argv, *, body=None, timeout=25):
    try:
        completed = subprocess.run(argv, input=body, text=True,
                                   capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        # Do not print exceptions, subprocess input, or raw device errors.
        raise PairError('La herramienta no respondió; comprobar estado antes de reintentar.') from None
    if completed.returncode != 0:
        raise PairError('La herramienta devolvió un error; comprobar conexión y estado.')
    return completed.stdout


def parse_provider(output):
    match = re.fullmatch(r'Result: Bundle\[\{json=(\{.*\})\}\]', output.strip(), re.S)
    if not match:
        raise PairError('El provider no devolvió una respuesta válida; no se muestra su salida sin filtrar.')
    try:
        value = json.loads(match.group(1))
    except (ValueError, TypeError):
        raise PairError('La respuesta del provider no es JSON válido.') from None
    if not isinstance(value, dict):
        raise PairError('Formato de respuesta inesperado.')
    return {key: value[key] for key in SAFE_FIELDS if key in value}


def transport():
    output = invoke(['adb.exe', 'devices', '-l'])
    matches = re.findall(r'^\S+\s+device\s+.*\bmodel:SM_S918B\b.*\btransport_id:(\d+)\s*$', output, re.M)
    if len(matches) != 1:
        raise PairError('Se necesita exactamente un SM-S918B autorizado por ADB.')
    return matches[0]


def provider(adb_transport, method, request):
    if method not in ('status', 'pair'):
        raise PairError('Método no permitido.')
    encoded = base64.b64encode(json.dumps(request, ensure_ascii=False,
                                        separators=(',', ':')).encode()).decode()
    if len(encoded) > 8192:
        raise PairError('Solicitud demasiado larga.')
    if method == 'pair':
        # The secret is only stdin; argv and script contain no payload.
        output = invoke(['adb.exe', '-t', adb_transport, 'shell', PAIR_COMMAND],
                        body=encoded + '\n')
    else:
        output = invoke(['adb.exe', '-t', adb_transport, 'shell', 'content', 'call',
                         '--uri', URI, '--method', 'status', '--arg', encoded])
    return parse_provider(output)


def public_key():
    policy = invoke(['ssh', '-G', 'mestry-s23'])
    fields = dict(line.split(None, 1) for line in policy.splitlines() if ' ' in line)
    if fields.get('port') != '8023' or fields.get('stricthostkeychecking') not in ('true', 'yes'):
        raise PairError('El alias mestry-s23 debe usar 8023 y confianza estricta.')
    script = """set -eu
[ "${SSH_CONNECTION##* }" = 8023 ]
[ "$(sshd -T | awk 'tolower($1)=="port" {print $2}')" = 8023 ]
awk '$1=="ssh-ed25519" && $3=="mestry-s25" {print}' "$HOME/.ssh/authorized_keys"
"""
    output = invoke(SSH + ['mestry-s23', 'sh -s'], body=script)
    lines = output.strip().splitlines()
    if len(lines) != 1:
        raise PairError('No se encontró una única clave pública mestry-s25.')
    parts = lines[0].split()
    if len(parts) != 3 or parts[0] != 'ssh-ed25519' or parts[2] != 'mestry-s25':
        raise PairError('Formato de clave pública S25 inesperado.')
    try:
        blob = base64.b64decode(parts[1], validate=True)
    except ValueError:
        raise PairError('Clave pública S25 inválida.') from None
    expected_prefix = struct.pack('>I', 11) + b'ssh-ed25519' + struct.pack('>I', 32)
    if len(blob) != 51 or not blob.startswith(expected_prefix):
        raise PairError('El blob no es una clave Ed25519 válida.')
    fingerprint = 'SHA256:' + base64.b64encode(hashlib.sha256(blob).digest()).decode().rstrip('=')
    if fingerprint != S25_FP:
        raise PairError('La huella no coincide con la clave S25 ya verificada.')
    return {'keyType': parts[0], 'keyData': parts[1], 'label': 'mestry-s25'}


def execute(report, *, check=False):
    adb_transport = transport()
    key = public_key()
    before = provider(adb_transport, 'status', {'fingerprint': S25_FP})
    report['before'] = before
    if before.get('status') != 'ok' or before.get('configured') is not True:
        raise PairError('Horus debe estar instalado y tener su contraseña local configurada.')
    if before.get('appVersion') != '1.0.4' or before.get('port') != 8022 or before.get('username') != 'horus':
        raise PairError('La versión o el perfil de Horus cambió; revisar antes de emparejar.')
    if check:
        report['status'] = 'PREFLIGHT_PASS'
        print('MESTRY_HORUS_S25_PREFLIGHT=PASS; no se solicitó contraseña ni se cambió el teléfono.')
        return
    if before.get('authorized') is True:
        report['status'] = 'ALREADY_AUTHORIZED'
        print('La clave S25 ya está autorizada; no se repite el emparejamiento.')
        return
    if not sys.stdin.isatty():
        raise PairError('Ejecutar en una terminal WSL interactiva; no introducir contraseñas por chat o tuberías.')
    print('Se añadirá únicamente la clave pública existente del S25: ' + S25_FP)
    print('El emparejamiento oficial también activa el remoto Horus en loopback 8022.')
    password = getpass.getpass('Contraseña LOCAL de Horus (no la de Google/OpenAI; no se mostrará): ')
    if not password:
        raise PairError('Contraseña vacía; no se envió ninguna solicitud de emparejamiento.')
    report['pair_requested_utc'] = now()
    report['pair_outcome'] = 'unknown_until_response'
    try:
        paired = provider(adb_transport, 'pair', {**key, 'password': password})
    finally:
        del password
    report['pair_response'] = paired
    report['pair_outcome'] = paired.get('status', 'unknown')
    if paired.get('status') != 'ok':
        if paired.get('status') == 'incorrect':
            raise PairError('Contraseña incorrecta; se realizó un solo intento, sin reintentos automáticos.')
        if paired.get('status') == 'locked':
            raise PairError('Horus tiene bloqueados temporalmente los intentos; no se reintenta.')
        raise PairError('Horus no confirmó el emparejamiento; comprobar estado antes de reintentar.')
    if paired.get('fingerprint') != S25_FP:
        raise PairError('El provider devolvió una huella distinta; comprobar el estado.')
    after = provider(adb_transport, 'status', {'fingerprint': S25_FP})
    report['after'] = after
    if after.get('status') != 'ok' or after.get('authorized') is not True:
        raise PairError('No se pudo verificar la autorización posterior; comprobar estado antes de reintentar.')
    report['status'] = 'PAIRED_VERIFIED'
    print('MESTRY_HORUS_S25_PAIR=PASS')
    print('La clave S25 está autorizada. Estado del servicio: ' + str(after.get('state', 'unknown')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Solo comprobar, sin contraseña ni mutaciones.')
    args = parser.parse_args()
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    root = Path(__file__).resolve().parents[1]
    out = root / 'docs/validation' / ('mestry-horus-pair-' + stamp)
    out.mkdir(mode=0o700)
    report = {'started_utc': now(), 'status': 'STARTED', 'check_only': args.check,
              'key_fingerprint': S25_FP, 'label': 'mestry-s25',
              'tool_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'Pair existing S25 public key only; official provider; no private-key transfer.'}
    exit_code = 0
    try:
        execute(report, check=args.check)
    except (EOFError, KeyboardInterrupt):
        report.update(status='INTERRUPTED', error='Interrumpido; comprobar estado si se alcanzó a enviar la solicitud.')
        print(report['error'], file=sys.stderr)
        exit_code = 1
    except PairError as error:
        report.update(status='FAILED_OR_UNVERIFIED', error=str(error))
        print(str(error), file=sys.stderr)
        exit_code = 1
    except Exception:
        report.update(status='FAILED_OR_UNVERIFIED', error='Error inesperado; salida sin filtrar omitida.')
        print(report['error'], file=sys.stderr)
        exit_code = 1
    finally:
        report['ended_utc'] = now()
        (out / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print('Registro sin contraseña: ' + str(out / 'result.json'))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())

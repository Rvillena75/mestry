#!/usr/bin/env python3
"""User terminal only: grant an existing folder with Google Picker, drive.file only.

Retains the active token throughout consent; saves a private backup on Termux.
Uses the existing Desktop client and already approved callback, not Android OAuth.
Never run this program through an evidence logger, tee, or a chat tool.
"""
import argparse
import datetime
import json
import logging
from pathlib import Path
import re
import shlex
import subprocess
import sys
import types
import urllib.request

from oauth_setup import validate_client
from publisher import ACCOUNT, Drive, FOLDER_MIME, NoRedirect, PublishError, SCOPE

SSH = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'ControlMaster=no', '-o', 'ControlPath=none', '-o', 'IdentityAgent=none', 'mestry-s23']

REMOTE = r'''
import contextlib,fcntl,json,os,pathlib,sys,types,urllib.request
os.umask(0o077)
if os.getuid()!=10348:raise SystemExit('TERMUX_PROFILE_REQUIRED')
sys.path.insert(0,str(pathlib.Path.home()/'.local/lib/mestry-publish'))
from publisher import STATE,SCOPE,Drive,NoRedirect,PublishError,private_path,read_private,require_account,write_private
from oauth_setup import validate_client
try:
 obj=json.load(sys.stdin)
 client=validate_client(read_private(STATE/'client.json'))['installed']
 active=json.loads(read_private(STATE/'token.json'))
 if active.get('client_id')!=client['client_id'] or obj['client_id']!=client['client_id']:raise PublishError('EXISTING_CLIENT_MISMATCH')
 if set(active.get('scopes',[]))!={SCOPE}:raise PublishError('EXISTING_SCOPE_MISMATCH')
 backup=STATE/obj['backup_name']
 if backup.parent!=STATE or not backup.name.startswith('token.pre-picker.'):raise PublishError('BACKUP_PATH_INVALID')
 if obj['action']=='backup':
  if backup.exists() or backup.is_symlink():raise PublishError('PRIVATE_BACKUP_ALREADY_EXISTS')
  write_private(backup,read_private(STATE/'token.json'))
  result={'status':'CURRENT_TOKEN_BACKED_UP_PRIVATELY','active_token_preserved':True}
 else:
  private_path(backup)
  token=obj['token']
  if (set(token.get('scopes',[]))!={SCOPE} or token.get('client_id')!=client['client_id']
      or token.get('client_secret')!=client['client_secret'] or token.get('token_uri')!='https://oauth2.googleapis.com/token'
      or not token.get('refresh_token')):raise PublishError('TOKEN_CLIENT_OR_SCOPE_MISMATCH')
  d=Drive.__new__(Drive);d.path=STATE;d.opener=urllib.request.build_opener(NoRedirect())
  token=d.refresh(token);d.creds=types.SimpleNamespace(token=token['token']);require_account(d)
  sys.path.insert(0,str(pathlib.Path.home()/'.local/lib/mestry-publish'))
  from drive_browser import metadata,load_state,PROJECT
  folder=metadata(d,obj['folder_id'],folder=True)
  fd=os.open(STATE/'drive-browser.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   state=load_state(STATE)
   if obj['folder_id'] not in state['enabled']:state['enabled'].append(obj['folder_id'])
   state['assignments'][PROJECT]=obj['folder_id']
   # Leave deleted pilot folders in Drive exactly as the user chose.
   old='DRIVE_FOLDER_01_EXAMPLE'
   if old!=obj['folder_id'] and old in state['enabled']:
    try:old_meta=d.metadata(old)
    except PublishError:old_meta={}
    if old_meta.get('trashed') is True:state['enabled'].remove(old)
   write_private(STATE/'token.json',json.dumps(token).encode())
   write_private(STATE/'drive-browser.json',json.dumps(state).encode())
  result={'status':'PICKER_AUTHORIZATION_SAVED','scope':'drive.file','folder_name':folder['name'],
          'native_refresh_verified':True,'private_backup_retained':True,'existing_client_preserved':True,
          'folder_assigned_to_project':True,'drive_files_created_or_restored':False}
 print(json.dumps(result))
except PublishError as error:
 print(json.dumps({'status':'ERROR','code':str(error)}));sys.exit(1)
except Exception:
 print(json.dumps({'status':'ERROR','code':'PRIVATE_PICKER_IMPORT_FAILED_NO_SECRET_DETAILS'}));sys.exit(1)
'''


def remote(payload):
    result = subprocess.run(SSH + ['python3 -I -c ' + shlex.quote(REMOTE)],
                            input=json.dumps(payload).encode(), capture_output=True, timeout=100)
    try:
        value = json.loads(result.stdout)
    except Exception:
        raise PublishError('PRIVATE_PICKER_SSH_FAILED_NO_SECRET_DETAILS') from None
    if result.returncode or value.get('status') == 'ERROR':
        code = value.get('code', '')
        raise PublishError(code if re.fullmatch('[A-Z0-9_]+', code) else 'PRIVATE_PICKER_IMPORT_FAILED')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('client_json', type=Path)
    parser.add_argument('--folder-id', required=True)
    parser.add_argument('--allow-loopback-53682', action='store_true')
    args = parser.parse_args()
    if not args.allow_loopback_53682:
        raise PublishError('EXISTING_CALLBACK_APPROVAL_REQUIRED')
    if not re.fullmatch('[A-Za-z0-9_-]{10,100}', args.folder_id):
        raise PublishError('FOLDER_ID_INVALID')
    client_path = args.client_json.resolve(strict=True)
    if client_path.is_relative_to(Path(__file__).resolve().parents[2]):
        raise PublishError('CLIENT_JSON_MUST_STAY_OUTSIDE_PROJECT')
    client = validate_client(client_path.read_bytes())
    backup = 'token.pre-picker.' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json'
    base = {'client_id': client['installed']['client_id'], 'backup_name': backup}
    remote(dict(base, action='backup'))
    from google_auth_oauthlib.flow import InstalledAppFlow
    logging.disable(logging.CRITICAL)
    flow = InstalledAppFlow.from_client_config(client, [SCOPE], autogenerate_code_verifier=True)
    print('Selecciona la carpeta MESTRY en Google. Plazo: 180 segundos. El token actual sigue activo.', flush=True)
    try:
        creds = flow.run_local_server(host='127.0.0.1', port=53682, open_browser=False, timeout_seconds=180,
            authorization_prompt_message='Abre este enlace solo en el navegador del PC: {url}',
            success_message='MESTRY recibió la selección. Vuelve a la terminal WSL.',
            access_type='offline', prompt='consent', include_granted_scopes='false', login_hint=ACCOUNT,
            trigger_onepick='true', allow_folder_selection='true', allow_multiple='true',
            file_ids=args.folder_id, mimetypes=FOLDER_MIME)
    except Exception:
        raise PublishError('PICKER_NOT_COMPLETED_PREVIOUS_TOKEN_PRESERVED') from None
    scopes = flow.oauth2session.token.get('scope', [])
    if isinstance(scopes, str): scopes = scopes.split()
    if set(scopes) != {SCOPE} or not creds.refresh_token:
        raise PublishError('PICKER_SCOPE_OR_REFRESH_TOKEN_MISMATCH')
    checker = Drive.__new__(Drive)
    checker.creds = creds
    checker.opener = urllib.request.build_opener(NoRedirect())
    if checker.account().lower() != ACCOUNT:
        raise PublishError('PICKER_ACCOUNT_MISMATCH_PREVIOUS_TOKEN_PRESERVED')
    token = json.loads(creds.to_json())
    result = remote(dict(base, action='commit', token=token, folder_id=args.folder_id))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except PublishError as error:
        print(json.dumps({'status': 'ERROR', 'code': str(error)}))
        raise SystemExit(1)
    except Exception:
        print(json.dumps({'status': 'ERROR', 'code': 'PRIVATE_PICKER_FAILED_PREVIOUS_TOKEN_PRESERVED'}))
        raise SystemExit(1)

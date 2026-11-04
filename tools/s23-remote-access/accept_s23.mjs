// Run inside the existing Horus profile; never exports its pairing key or history.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const root = '/workspace/projects/mestry';
const pause = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const fixedError = (code) => new Error(code);

export function terminalMatches(message, session, turn) {
  return message?.event === 'turn/completed' && message.session_id === session &&
    (message.turn_id ?? message.payload?.turn?.id) === turn;
}

export function toolReceipts(content, expectedHead) {
  let head = false;
  let preview = false;
  let commands = 0;
  function visit(value, depth = 0) {
    if (!value || typeof value !== 'object' || depth > 24) return;
    if (value.type === 'commandExecution') {
      commands += 1;
      if (value.exitCode !== 0 || value.status !== 'completed') return;
      const output = value.aggregatedOutput ?? value.stdout ?? value.output ?? '';
      if (typeof output === 'string') for (const line of output.split('\n')) {
        try {
          const item = JSON.parse(line);
          if (item.marker === 'S23_BRIDGE_COMMAND_READY' && item.head === expectedHead) head = true;
          if (item.action === 'finish' && item.state === 'OK' && item.index_unchanged === true &&
              item.plan?.publication_requested === false && item.plan?.changed?.length === 0) preview = true;
        } catch { /* Tool text is data; never evaluate it. */ }
      }
      return;
    }
    // An assistant quoting a receipt is not evidence of command execution.
    if (value.type === 'agentMessage' || value.type === 'userMessage') return;
    for (const child of Object.values(value)) visit(child, depth + 1);
  }
  visit(content);
  return { command_head_verified: head, within_turn_preview_verified: preview, command_items: commands };
}

function command(args, timeout = 60000) {
  const result = spawnSync(args[0], args.slice(1), { cwd: root, encoding: 'utf8',
    timeout, maxBuffer: 2000000, stdio: ['ignore', 'pipe', 'ignore'] });
  let value;
  try { value = JSON.parse(result.stdout.trim().split('\n').at(-1)); }
  catch { throw fixedError('LOCAL_METADATA_RESULT_UNAVAILABLE'); }
  return { exit: result.status, value };
}

function check() { return command(['sh', 'tools/work-session.sh', 'check', '--remote']).value; }

function privateFile(file) {
  const info = fs.lstatSync(file);
  if (!info.isFile() || info.isSymbolicLink() || info.uid !== process.getuid() || (info.mode & 0o077)) {
    throw fixedError('PRIVATE_PROFILE_FILE_REQUIRED');
  }
  return fs.readFileSync(file, 'utf8');
}

function socketClient(WebSocket, token) {
  const ws = new WebSocket('ws://127.0.0.1:8787/', { headers: { 'X-Bridge-Token': token } });
  const messages = [];
  const pending = new Map();
  let counter = 0;
  ws.on('message', (raw) => {
    if (raw.length > 4000000) return;
    let message;
    try { message = JSON.parse(raw.toString()); } catch { return; }
    if (messages.length < 6000) messages.push(message);
    const waiter = pending.get(message.id);
    if (waiter) {
      pending.delete(message.id);
      clearTimeout(waiter.timer);
      if (message.ok !== true) waiter.reject(fixedError('BRIDGE_REQUEST_REJECTED'));
      else waiter.resolve(message.payload);
    }
  });
  ws.on('error', () => {});
  const ready = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(fixedError('BRIDGE_CONNECT_TIMEOUT')), 10000);
    ws.once('open', () => { clearTimeout(timer); resolve(); });
    ws.once('error', () => { clearTimeout(timer); reject(fixedError('BRIDGE_CONNECT_FAILED')); });
  });
  return { ws, messages, ready,
    request(type, payload = {}, timeout = 60000) {
      const id = 's23-acceptance-' + (++counter);
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => { pending.delete(id); reject(fixedError('BRIDGE_REQUEST_TIMEOUT')); }, timeout);
        pending.set(id, { resolve, reject, timer });
        ws.send(JSON.stringify({ id, type, payload }), (error) => {
          if (error && pending.delete(id)) { clearTimeout(timer); reject(fixedError('BRIDGE_SEND_FAILED')); }
        });
      });
    },
    close() {
      for (const waiter of pending.values()) { clearTimeout(waiter.timer); waiter.reject(fixedError('BRIDGE_CONNECTION_CLOSED')); }
      pending.clear();
      ws.terminate();
    } };
}

async function main() {
  process.umask(0o077);
  if (os.homedir() !== '/home/horus' || process.getuid() !== 1000 || process.arch !== 'arm64') {
    throw fixedError('EXISTING_HORUS_PROFILE_REQUIRED');
  }
  const directory = path.join(os.homedir(), '.local/state/mestry-s23-checks');
  fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
  const info = fs.lstatSync(directory);
  if (!info.isDirectory() || info.isSymbolicLink() || (info.mode & 0o077)) throw fixedError('PRIVATE_OUTPUT_REQUIRED');
  const report = { marker: 'MESTRY_S23_ACCEPTANCE', started_utc: new Date().toISOString(),
    model_turns_started: 0, configuration_changed: false, raw_history_exported: false, s25_client_accepted: false };
  function emit() {
    const data = JSON.stringify(report);
    fs.writeFileSync(path.join(directory, 'result.json'), data + '\n', { mode: 0o600 });
    console.log(data);
    spawnSync('/system/bin/log', ['-p', 'i', '-t', 'MESTRY_S23_CHECKS', data], { stdio: 'ignore', timeout: 5000 });
  }
  let client;
  let active = null;
  try {
    const before = check();
    if (before.state !== 'OK' || before.busy || before.dirty || before.recovery_required || before.environment_error) {
      throw fixedError('CLEAN_FREE_ADMITTED_PROJECT_REQUIRED');
    }
    report.head_before = before.head;
    report.remote_head = before.remote_head;
    if (!/^[a-f0-9]{40}$/.test(before.remote_head ?? '')) throw fixedError('REMOTE_HEAD_REQUIRED');
    const keeper = JSON.parse(fs.readFileSync(path.join(os.homedir(), '.local/state/mestry-keepalive/status.json'), 'utf8'));
    report.supervisor = { state: keeper.state, checked_utc: keeper.checked_utc,
      consecutive_failures: keeper.consecutive_failures,
      project_poll_state: keeper.project_poll?.state,
      project_states: keeper.project_poll?.projects?.map((p) => ({ state: p.state, head: p.head, remote: p.remote, update_pending: p.update_pending })) };
    const base = path.join(os.homedir(), '.local/lib/mestry-s25-pilot');
    const release = JSON.parse(privateFile(path.join(base, 'current.json'))).directory;
    if (path.dirname(release) !== path.join(base, 'releases')) throw fixedError('INSTALLED_RELEASE_REQUIRED');
    const require = createRequire(path.join(release, 'src/mestry-entry.mjs'));
    const WebSocket = require('ws');
    const token = privateFile(path.join(os.homedir(), '.local/state/mestry-s25-client/bridge-token')).trim();
    if (!/^[A-Za-z0-9_-]{43,128}$/.test(token)) throw fixedError('EXISTING_PAIRING_REQUIRED');
    client = socketClient(WebSocket, token);
    await client.ready;
    await client.request('ping');
    report.authenticated_hello = client.messages.some((m) => m.type === 'hello' && m.ok === true && m.payload?.name === 'mestry-s25-pilot');
    report.phase = 'preparing_thread'; emit();
    const started = await client.request('session.start', { cwd: root }, 910000);
    const session = started.session?.session_id;
    if (typeof session !== 'string' || started.session?.cwd !== root) throw fixedError('PROJECT_SESSION_REQUIRED');
    report.thread_sha256 = crypto.createHash('sha256').update(session).digest('hex');
    const afterEntry = check();
    report.head_received = afterEntry.head;
    report.validation_matches_head = afterEntry.validation_matches_head;
    report.entry_application = { method: 'session.start', head_before: before.head, head_after: afterEntry.head,
      applied_new_revision: before.head !== afterEntry.head };
    report.target_validation = afterEntry.validation;
    if (afterEntry.head !== before.remote_head || !afterEntry.validation_matches_head || afterEntry.dirty) {
      throw fixedError('VALIDATED_REMOTE_RECEIPT_REQUIRED');
    }
    const prompt = 'S23 bridge acceptance. Read AGENTS.md and STATUS.md. Do not edit files, publish, install, change settings, use other projects or read credentials. Execute python3 -c \'import subprocess,time,json; print(json.dumps({"marker":"S23_BRIDGE_COMMAND_READY","head":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()})); time.sleep(10)\'. Then execute sh tools/work-session.sh --within-turn finish README.md as a preview only. Do not start another wrapper. Finally respond S23_BRIDGE_ACCEPTED.';
    const sent = await client.request('turn.send', { session_id: session, text: prompt });
    const turn = sent.turn?.id;
    if (typeof turn !== 'string') throw fixedError('TURN_ID_REQUIRED');
    active = { session, turn };
    report.model_turns_started = 1;
    const competing = command(['sh', 'tools/work-session.sh', 'receive', '--fetch-only']);
    report.competing_writer_rejected = competing.exit === 3 && competing.value.reason === 'BUSY';
    report.phase = 'turn_running'; emit();
    const deadline = Date.now() + 240000;
    while (!client.messages.some((m) => terminalMatches(m, session, turn))) {
      if (Date.now() > deadline) throw fixedError('TURN_COMPLETION_TIMEOUT');
      await pause(200);
    }
    const completed = client.messages.find((m) => terminalMatches(m, session, turn));
    report.turn_status = completed.payload?.turn?.status ?? completed.payload?.status ?? null;
    active = null;
    client.close();
    client = socketClient(WebSocket, token);
    await client.ready;
    const content = await client.request('session.content', { session_id: session });
    const synced = await client.request('session.sync', { session_id: session, since_seq: 0 });
    report.fresh_authenticated_history_response = true;
    report.history_entries = Array.isArray(content.entries) ? content.entries.length : 0;
    report.sync_entries = Array.isArray(synced.entries) ? synced.entries.length : 0;
    Object.assign(report, toolReceipts(content, afterEntry.head));
    let final;
    for (let attempt = 0; attempt < 10; attempt++) {
      final = check();
      if (!final.busy) break;
      await pause(300);
    }
    report.final = { head: final.head, busy: final.busy, dirty: final.dirty, phase: final.phase,
      recovery_required: final.recovery_required, failed_candidate: Boolean(final.failed_candidate),
      validation_matches_head: final.validation_matches_head };
    report.status = report.authenticated_hello && report.competing_writer_rejected && report.command_head_verified &&
      report.within_turn_preview_verified && report.turn_status === 'completed' && !final.busy && !final.dirty &&
      !final.recovery_required && !final.failed_candidate && final.head === afterEntry.head &&
      final.validation_matches_head && final.phase === 'idle' ? 'PASS' : 'INCOMPLETE';
    report.phase = 'finished';
  } catch (error) {
    report.status = 'BLOCKED';
    report.reason = /^[A-Z_0-9]+$/.test(error.message) ? error.message : 'CHECK_FAILED_NO_PRIVATE_DETAILS';
    if (active && client) {
      try {
        await client.request('turn.interrupt', { session_id: active.session, turn_id: active.turn }, 10000);
        const deadline = Date.now()+30000;
        while (!client.messages.some((m) => terminalMatches(m, active.session, active.turn)) && Date.now()<deadline) await pause(200);
        report.own_turn_termination_confirmed = client.messages.some((m) => terminalMatches(m, active.session, active.turn));
      } catch { report.own_turn_termination_confirmed = false; }
    }
  } finally {
    client?.close();
    report.ended_utc = new Date().toISOString();
    emit();
  }
  process.exitCode = report.status === 'PASS' ? 0 : 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main().catch(() => { console.error('S23_CHECK_FAILED_NO_PRIVATE_DETAILS'); process.exitCode = 1; });
}

// A fake stdio executable checks the ordering used by the actual Node backend.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { CodexBackend } from '../src/backends/codex.mjs';

test('backend sends initialized before requests and verifies actual thread policy before a turn', async (t) => {
  const temp = await fs.mkdtemp(path.join(os.tmpdir(), 'mestry-jsonl-'));
  const script = path.join(temp, 'fake-codex');
  await fs.writeFile(script, `#!/usr/bin/env node
import readline from 'node:readline';
let initialized = false;
const root = process.env.MESTRY_FIXTURE_PROJECT;
for await (const line of readline.createInterface({ input: process.stdin })) {
  const m = JSON.parse(line);
  if (m.method === 'initialized') { initialized = true; continue; }
  let result = {};
  if (m.method !== 'initialize' && !initialized) { process.stdout.write(JSON.stringify({id:m.id,error:{code:-32600,message:'initialized missing'}})+'\\n'); continue; }
  if (m.method === 'account/read') result = { account: { type: 'chatgpt' } };
  if (m.method === 'thread/list') result = { data: [], nextCursor: null };
  if (m.method === 'thread/start') result = { thread: { id: 'fixture-thread', cwd: root }, cwd: root, approvalPolicy: m.params.approvalPolicy, extended: m.params.persistExtendedHistory, sandbox: { type: 'dangerFullAccess' } };
  if (m.method === 'turn/start') result = { turn: { id: 'fixture-turn', params: m.params } };
  process.stdout.write(JSON.stringify({ id:m.id, result })+'\\n');
}
`, { mode: 0o700 });
  const previous = process.env.MESTRY_FIXTURE_PROJECT;
  process.env.MESTRY_FIXTURE_PROJECT = temp;
  const backend = new CodexBackend({ codexBin: script, pilotProject: temp, requestTimeoutMs: 2500 });
  t.after(async () => { await backend.stop(); if (previous == null) delete process.env.MESTRY_FIXTURE_PROJECT; else process.env.MESTRY_FIXTURE_PROJECT = previous; await fs.rm(temp, { recursive: true, force: true }); });
  await backend.start();
  assert.deepEqual(await backend.listThreads(), []);
  await assert.rejects(backend.startTurn('unverified', { text: 'fixture' }), /VERIFIED_THREAD_REQUIRED/);
  const started = await backend.startThread({ approvalPolicy: 'on-request', sandbox: 'workspace-write', persistExtendedHistory: false });
  assert.equal(started.approvalPolicy, 'never');
  assert.equal(started.extended, true);
  const result = await backend.startTurn('fixture-thread', { text: 'fixture', approvalPolicy: 'never' });
  assert.equal(result.turn.params.approvalPolicy, 'never');
  assert.deepEqual(result.turn.params.sandboxPolicy, { type: 'dangerFullAccess' });
  assert.equal(result.turn.params.cwd, temp);
});

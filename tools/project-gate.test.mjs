import test from 'node:test';
import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import { guardBackend } from './project-gate.mjs';

class FixtureGate {
  constructor() { this.held = false; this.released = 0; this.abandoned = false; }
  async acquire() {
    if (this.held || this.abandoned) throw new Error('BUSY');
    this.held = true;
  }
  async release() { assert.equal(this.held, true); this.held = false; this.released++; }
  abandon() { this.abandoned = true; }
}

function fixture({ beforeReply, fail = false, result = { turn: { id: 'new-turn' } } } = {}) {
  const gate = new FixtureGate();
  const backend = new EventEmitter();
  backend.startThread = async () => ({ thread: { id: 'thread' } });
  backend.resumeThread = backend.startThread;
  backend.startTurn = async () => {
    assert.equal(gate.held, true);
    await beforeReply?.(backend);
    if (fail) throw new Error('Fixture timeout');
    return result;
  };
  backend.steerTurn = async () => 'steered';
  backend.interruptTurn = async () => 'interrupted';
  guardBackend(backend, { gate });
  return { backend, gate };
}
const complete = (backend, threadId = 'thread', id = 'new-turn') => backend.emit('message', {
  method: 'turn/completed', params: { threadId, turn: { id } },
});
const settled = () => new Promise((resolve) => setImmediate(resolve));

test('thread start and resume release their metadata operation lock', async () => {
  const { backend, gate } = fixture();
  await backend.startThread(); await backend.resumeThread('thread');
  assert.equal(gate.released, 2); assert.equal(gate.held, false);
});
test('turn keeps lock after RPC acknowledgement and rejects a second writer', async () => {
  const { backend, gate } = fixture();
  await backend.startTurn('thread');
  assert.equal(gate.held, true); assert.equal(gate.released, 0);
  await assert.rejects(backend.startTurn('other'), /BUSY/);
  await assert.rejects(backend.startThread(), /BUSY/);
  complete(backend); await settled(); assert.equal(gate.held, false);
});
test('foreign thread and old-turn notifications cannot release the current lock', async () => {
  const { backend, gate } = fixture();
  await backend.startTurn('thread'); complete(backend, 'foreign'); complete(backend, 'thread', 'old-turn');
  await settled(); assert.equal(gate.held, true);
  complete(backend); await settled(); assert.equal(gate.released, 1);
});
test('terminal notification before RPC result is reconciled by exact turn ID', async () => {
  const { backend, gate } = fixture({ beforeReply: async (b) => complete(b) });
  await backend.startTurn('thread'); assert.equal(gate.released, 1);
});
test('duplicate terminal notifications release only once', async () => {
  const { backend, gate } = fixture();
  await backend.startTurn('thread'); complete(backend); complete(backend); await settled();
  assert.equal(gate.released, 1);
});
test('ambiguous RPC failure abandons rather than assuming the writer stopped', async () => {
  const { backend, gate } = fixture({ fail: true });
  await assert.rejects(backend.startTurn('thread'), /Fixture timeout/);
  assert.equal(gate.abandoned, true); assert.equal(gate.released, 0);
});
test('missing effective turn ID requires recovery', async () => {
  const { backend, gate } = fixture({ result: {} });
  await assert.rejects(backend.startTurn('thread'), /TURN_ID_REQUIRED/);
  assert.equal(gate.abandoned, true);
});
test('steer and interrupt must target the held turn', async () => {
  const { backend } = fixture();
  await backend.startTurn('thread');
  assert.equal(await backend.interruptTurn('thread', 'new-turn'), 'interrupted');
  await assert.rejects(backend.steerTurn('other', 'new-turn'), /ACTIVE_TURN_REQUIRED/);
  await assert.rejects(backend.interruptTurn('thread', 'old-turn'), /ACTIVE_TURN_REQUIRED/);
});
test('backend death does not release a potentially live writer', async () => {
  const { backend, gate } = fixture();
  await backend.startTurn('thread');
  backend.emit('message', { method: 'error', params: { code: 'codex_process_exit' } });
  assert.equal(gate.abandoned, true); assert.equal(gate.released, 0);
});

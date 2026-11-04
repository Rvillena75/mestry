import test from 'node:test';
import assert from 'node:assert/strict';
import { terminalMatches, toolReceipts } from './accept_s23.mjs';

test('completion must identify the exact new thread and turn', () => {
  const event = { event: 'turn/completed', session_id: 'own', turn_id: 'turn' };
  assert.equal(terminalMatches(event, 'own', 'turn'), true);
  assert.equal(terminalMatches(event, 'other', 'turn'), false);
  assert.equal(terminalMatches(event, 'own', 'other'), false);
  assert.equal(terminalMatches({ ...event, event: 'turn/started' }, 'own', 'turn'), false);
});

test('assistant claims and incorrect HEAD cannot pass the tool receipt check', () => {
  const receipt = JSON.stringify({ marker: 'S23_BRIDGE_COMMAND_READY', head: 'correct' });
  const quoted = { entries: [{ type: 'agentMessage', output: receipt }] };
  assert.equal(toolReceipts(quoted, 'correct').command_head_verified, false);
  assert.equal(toolReceipts({ type: 'commandExecution', exitCode: 0, status: 'completed', aggregatedOutput: receipt }, 'other').command_head_verified, false);
});

test('only a real tool receipt with an unchanged index and no publication passes', () => {
  const preview = { action: 'finish', state: 'OK', index_unchanged: true,
    plan: { publication_requested: false, changed: [] } };
  const output = (value) => ({ type: 'commandExecution', exitCode: 0, status: 'completed', aggregatedOutput: JSON.stringify(value) });
  assert.equal(toolReceipts({ entries: [output(preview)] }, 'head').within_turn_preview_verified, true);
  assert.equal(toolReceipts(output({ ...preview, index_unchanged: false }), 'head').within_turn_preview_verified, false);
  assert.equal(toolReceipts(output({ ...preview, plan: { publication_requested: true, changed: [] } }), 'head').within_turn_preview_verified, false);
});

test('failed, unfinished or missing-exit commands cannot authenticate receipts', () => {
  const preview = JSON.stringify({ action: 'finish', state: 'OK', index_unchanged: true,
    plan: { publication_requested: false, changed: [] } });
  const head = JSON.stringify({ marker: 'S23_BRIDGE_COMMAND_READY', head: 'expected' });
  for (const state of [{ exitCode: 1, status: 'completed' }, { exitCode: 0, status: 'inProgress' }, {}]) {
    const result = toolReceipts({ type: 'commandExecution', ...state, aggregatedOutput: head + '\n' + preview }, 'expected');
    assert.equal(result.command_head_verified, false);
    assert.equal(result.within_turn_preview_verified, false);
  }
});

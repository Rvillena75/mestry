import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { authenticated, PilotPolicy, verifyEffectiveHorusPolicy } from './pilot-policy.mjs';

test('effective policy requires actual response fields, including approvals', () => {
  assert.throws(() => verifyEffectiveHorusPolicy({}));
  assert.throws(() => verifyEffectiveHorusPolicy({ approvalPolicy: 'on-request', sandbox: { type: 'dangerFullAccess' } }));
  assert.throws(() => verifyEffectiveHorusPolicy({ approvalPolicy: 'on-request' }));
  verifyEffectiveHorusPolicy({ approvalPolicy: 'never', sandbox: { type: 'dangerFullAccess' } });
});

test('header authentication fails closed without disclosing credentials', () => {
  const token = 'unit_test_fixture_only_'.padEnd(48, 'x');
  assert.equal(authenticated({}, token), false);
  assert.equal(authenticated({ 'x-bridge-token': token }, ''), false);
  assert.equal(authenticated({ 'x-bridge-token': [token] }, token), false);
  assert.equal(authenticated({ 'x-bridge-token': token + 'x' }, token), false);
  assert.equal(authenticated({ 'x-bridge-token': token.replace('u', 'v') }, token), false);
  assert.equal(authenticated({ 'x-bridge-token': token }, token), true);
});

test('pilot confines paths and sessions, rejects alternate configuration and foreign approvals', async (t) => {
  const temp = await fs.mkdtemp(path.join(os.tmpdir(), 'mestry-policy-'));
  t.after(() => fs.rm(temp, { recursive: true, force: true }));
  const root = path.join(temp, 'project');
  const other = path.join(temp, 'project-sibling');
  await fs.mkdir(root); await fs.mkdir(other);
  await fs.writeFile(path.join(root, 'ok.txt'), 'fixture');
  await fs.writeFile(path.join(other, 'private.txt'), 'outside');
  await fs.symlink(other, path.join(root, 'escape'));
  const policy = new PilotPolicy(root);
  await policy.initialize();
  const own = { session_id: 'own', thread_id: 'own', cwd: root };
  const foreign = { session_id: 'foreign', thread_id: 'foreign', cwd: other };
  const store = { getSession: (id) => ({ own, foreign })[id], getPendingApproval: (id, request) => id === 'own' && request === 'real' ? {} : null };
  assert.equal(await policy.file('ok.txt', root), path.join(root, 'ok.txt'));
  await assert.rejects(policy.file('../project-sibling/private.txt', root));
  await assert.rejects(policy.file('escape/private.txt', root));
  await assert.rejects(policy.file(path.join(other, 'private.txt'), root));
  assert.deepEqual(await policy.filterThreads([{ id: 'own', cwd: root }, { id: 'foreign', cwd: other }]), [{ id: 'own', cwd: root }]);
  await assert.rejects(policy.prepare('session.resume', { session_id: 'unknown' }, store));
  await assert.rejects(policy.prepare('session.resume', { session_id: 'foreign' }, store));
  await assert.rejects(policy.prepare('turn.interrupt', { session_id: 'own', thread_id: 'foreign' }, store));
  await assert.rejects(policy.prepare('session.start', { cwd: root, config: {} }, store));
  await assert.rejects(policy.prepare('session.start', { cwd: root, config: { approval_policy: 'never' } }, store));
  const configured = await policy.prepare('session.start', { cwd: root, config: { model_reasoning_effort: 'high' } }, store);
  assert.deepEqual(configured.config, { model_reasoning_effort: 'high' });
  await assert.rejects(policy.prepare('session.start', { cwd: other }, store));
  await assert.rejects(policy.prepare('turn.send', { session_id: 'own', input: [{ type: 'localImage', path: '/private/image.png' }] }, store));
  await assert.rejects(policy.prepare('approval.response', { session_id: 'own', request_id: 'forged' }, store));
  await assert.rejects(policy.prepare('goal.set', { session_id: 'own', objective: 'unrequested autonomy' }, store));
  const turn = await policy.prepare('turn.send', { session_id: 'own', approvalPolicy: 'never', text: 'fixture' }, store);
  assert.equal(turn.approvalPolicy, 'never');
  assert.deepEqual(turn.sandboxPolicy, { type: 'dangerFullAccess' });
  assert.equal(turn.cwd, root);
  const start = await policy.prepare('session.start', {}, store);
  assert.equal(start.cwd, root);
  assert.equal(start.sandbox, 'danger-full-access');
  assert.equal(start.approvalPolicy, 'never');
});

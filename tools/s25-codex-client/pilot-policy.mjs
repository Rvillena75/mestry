// MESTRY pilot policy for the pinned codex-remote-control bridge.
// This is an application ACL. It is not an OS sandbox for Codex's tools.
import fs from 'node:fs/promises';
import path from 'node:path';
import { timingSafeEqual } from 'node:crypto';

export function authenticated(headers, token) {
  const supplied = headers?.['x-bridge-token'];
  if (typeof token !== 'string' || token.length < 32 || typeof supplied !== 'string') return false;
  const left = Buffer.from(supplied);
  const right = Buffer.from(token);
  return left.length === right.length && timingSafeEqual(left, right);
}

export function verifyEffectiveHorusPolicy(result) {
  // Require evidence in the real RPC response; do not label requested settings
  // as confirmed merely because they were sent to the child process.
  const sandbox = result?.sandbox;
  const mode = typeof sandbox === 'string' ? sandbox : sandbox?.type;
  if (result?.approvalPolicy !== 'never' || !['dangerFullAccess', 'danger-full-access'].includes(mode)) denied();
}

function denied() {
  const error = new Error('MESTRY_PILOT_REQUEST_DENIED');
  error.code = 'MESTRY_PILOT_REQUEST_DENIED';
  throw error;
}

export class PilotPolicy {
  constructor(projectRoot) {
    this.root = path.resolve(projectRoot);
  }

  async initialize() {
    this.root = await fs.realpath(this.root);
    if (!(await fs.stat(this.root)).isDirectory()) denied();
  }

  async project(cwd) {
    if (!cwd || typeof cwd !== 'string' || !path.isAbsolute(cwd)) denied();
    if (await fs.realpath(cwd) !== this.root) denied();
    return this.root;
  }

  async file(requested, cwd) {
    await this.project(cwd);
    if (!requested || typeof requested !== 'string') denied();
    const lexical = path.resolve(this.root, requested);
    const actual = await fs.realpath(lexical);
    for (const candidate of [lexical, actual]) {
      const relative = path.relative(this.root, candidate);
      if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) denied();
    }
    return actual;
  }

  async filterThreads(threads) {
    const result = [];
    for (const thread of threads) {
      try {
        await this.project(thread?.cwd);
        result.push(thread);
      } catch { /* do not reveal other projects */ }
    }
    return result;
  }

  async prepare(type, source, store) {
    const payload = { ...source };
    const independent = new Set(['ping', 'model.list', 'collaboration_mode.list', 'session.list', 'directory.list', 'session.start', 'drive.state', 'drive.folder.enable', 'drive.assign', 'drive.list', 'drive.read']);
    const scoped = new Set(['session.resume', 'session.update', 'session.sync', 'session.content', 'turn.send', 'turn.steer', 'turn.interrupt', 'approval.response', 'file.read']);
    if (!independent.has(type) && !scoped.has(type)) denied();

    // The existing Android new-chat flow sends this one model option.
    if (payload.config != null) {
      const config = payload.config;
      if (type !== 'session.start' || typeof config !== 'object' || Array.isArray(config) ||
          Object.keys(config).length !== 1 || !Object.hasOwn(config, 'model_reasoning_effort') ||
          !['', 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'].includes(config.model_reasoning_effort)) denied();
      if (config.model_reasoning_effort === '') payload.config = null;
    }
    for (const field of ['permissions', 'environments', 'dynamicTools', 'history', 'path',
      'baseInstructions', 'developerInstructions', 'modelProvider', 'approvalsReviewer', 'responsesapiClientMetadata']) {
      if (type === 'file.read' && field === 'path') continue;
      if (type === 'directory.list' && field === 'path') continue;
      if (payload[field] != null) denied();
    }

    let session;
    if (scoped.has(type)) {
      const id = payload.session_id ?? payload.thread_id;
      if (typeof id !== 'string' || !id) denied();
      session = store.getSession(id);
      if (!session || (payload.thread_id && payload.thread_id !== (session.thread_id ?? id))) denied();
      await this.project(session.cwd ?? session.thread?.cwd);
    }
    if (payload.cwd != null) await this.project(payload.cwd);
    if (['session.start', 'session.resume', 'turn.send'].includes(type)) payload.cwd = this.root;

    // Horus's explicitly accepted full-access runtime stays explicit. Never silently
    // infer the effective policy from missing response fields. The user explicitly
    // selected never approvals for this app on 2026-10-21.
    if (['session.start', 'session.resume', 'session.update', 'turn.send'].includes(type)) {
      payload.approvalPolicy = 'never';
      if (type === 'turn.send') payload.sandboxPolicy = { type: 'dangerFullAccess' };
      else payload.sandbox = 'danger-full-access';
    }
    if (payload.input != null) {
      if (!Array.isArray(payload.input) || payload.input.some((item) => item?.type !== 'text')) denied();
    }
    // Do not accept an arbitrary backend request id or a foreign-session approval.
    if (type === 'approval.response') {
      const requestId = payload.request_id ?? payload.requestId;
      if (!store.getPendingApproval(session.session_id, requestId)) denied();
    }
    if (type === 'file.read') payload.path = await this.file(payload.path, session.cwd ?? session.thread?.cwd);
    if (type === 'directory.list') {
      const requested = payload.path;
      if (requested && requested !== path.dirname(this.root)) await this.file(requested, this.root);
    }
    return payload;
  }
}

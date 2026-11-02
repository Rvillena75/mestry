// Cooperate with the existing local Git session lock; no server or credentials.
import { spawn } from 'node:child_process';
import path from 'node:path';
import readline from 'node:readline';

function denied(reason = 'PROJECT_GUARD_FAILED') {
  const safe = /^[A-Z_0-9]+$/.test(reason) ? reason : 'PROJECT_GUARD_FAILED';
  return new Error(`MESTRY_${safe}`);
}

export class ProjectGate {
  constructor(root, { python = 'python3', stateRoot = null, offline = false,
    applyOnEntry = false, timeoutMs = 900000, writerPid = () => null } = {}) {
    this.root = path.resolve(root);
    this.options = { python, stateRoot, offline, applyOnEntry, timeoutMs, writerPid };
    this.child = null;
    this.broken = false;
  }

  async acquire() {
    if (this.broken) throw denied('PROJECT_RECOVERY_REQUIRED');
    if (this.child) throw denied('BUSY');
    const options = this.options;
    const args = ['-B', path.join(this.root, 'tools/work_session.py'), '--repo', this.root];
    if (options.stateRoot) args.push('--state-root', options.stateRoot);
    args.push('lease');
    if (options.offline) args.push('--offline');
    if (!options.applyOnEntry) args.push('--observe-only');
    const writer = options.writerPid();
    if (Number.isInteger(writer) && writer > 1) args.push('--writer-pid', String(writer));
    const child = spawn(options.python, args, { cwd: this.root, stdio: ['pipe', 'pipe', 'ignore'] });
    this.child = child;
    this.closed = new Promise((resolve) => {
      child.once('error', () => resolve(-1));
      child.once('close', (code) => resolve(code ?? -1));
    });
    child.stdin.on('error', () => {});
    const lines = readline.createInterface({ input: child.stdout });
    try {
      return await new Promise((resolve, reject) => {
        let settled = false;
        let reason = 'PROJECT_GUARD_FAILED';
        const settle = (fn, value) => {
          if (settled) return;
          settled = true;
          clearTimeout(timer);
          fn(value);
        };
        const timer = setTimeout(() => {
          this.broken = true;
          child.stdin.end();
          settle(reject, denied('PROJECT_GUARD_TIMEOUT'));
        }, options.timeoutMs);
        lines.on('line', (line) => {
          let message;
          try { message = JSON.parse(line); } catch { return; }
          if (message.state === 'LEASE_READY') settle(resolve, message);
          if (message.state === 'BLOCKED') reason = message.reason;
        });
        this.closed.then(() => settle(reject, denied(reason)));
      });
    } catch (error) {
      child.stdin.end();
      // A failed acquisition never starts a backend writer. A timeout still
      // retains the child reference until its locked preparation finishes.
      if (!this.broken) {
        await this.closed;
        this.child = null;
      }
      throw error;
    }
  }

  async release() {
    if (!this.child || this.broken) throw denied('PROJECT_RECOVERY_REQUIRED');
    this.child.stdin.end('release\n');
    if (await this.closed !== 0) {
      this.broken = true;
      throw denied('PROJECT_RECOVERY_REQUIRED');
    }
    this.child = null;
  }

  abandon() {
    this.broken = true;
    this.child?.stdin.end();
  }
}

export function guardBackend(backend, { root, gate = new ProjectGate(root) } = {}) {
  if (gate.options) gate.options.writerPid = () => backend.child?.pid ?? null;
  let active = null;
  let closing = null;
  const releaseTurn = async (entry) => {
    if (active !== entry || closing) return;
    closing = gate.release();
    try { await closing; active = null; }
    catch { gate.abandon(); }
    finally { closing = null; }
  };
  const scoped = async (operation) => {
    await gate.acquire();
    try { return await operation(); }
    finally { await gate.release(); }
  };
  for (const name of ['startThread', 'resumeThread']) {
    const original = backend[name].bind(backend);
    backend[name] = (...args) => scoped(() => original(...args));
  }
  const originalTurn = backend.startTurn.bind(backend);
  backend.startTurn = async (threadId, ...args) => {
    if (active || closing) throw denied('BUSY');
    await gate.acquire();
    const entry = { threadId, turnId: null, completed: new Set() };
    active = entry;
    try {
      const result = await originalTurn(threadId, ...args);
      entry.turnId = result?.turn?.id;
      if (typeof entry.turnId !== 'string' || !entry.turnId) throw denied('TURN_ID_REQUIRED');
      if (entry.completed.has(entry.turnId)) await releaseTurn(entry);
      return result;
    } catch (error) {
      // A timed-out RPC may already have started a turn. Never infer inactivity.
      gate.abandon();
      throw error;
    }
  };
  for (const name of ['steerTurn', 'interruptTurn']) {
    const original = backend[name].bind(backend);
    backend[name] = async (threadId, turnId, ...args) => {
      if (!active || active.threadId !== threadId || active.turnId !== turnId) throw denied('ACTIVE_TURN_REQUIRED');
      return original(threadId, turnId, ...args);
    };
  }
  backend.on('message', (message) => {
    if (!active) return;
    const data = message?.params ?? {};
    if (message.method === 'error' && data.code === 'codex_process_exit') {
      gate.abandon();
      return;
    }
    if (message.method !== 'turn/completed') return;
    const threadId = data.threadId ?? data.thread_id;
    const turnId = data.turn?.id ?? data.turnId ?? data.turn_id;
    if (threadId !== active.threadId || typeof turnId !== 'string') return;
    if (active.turnId === turnId) void releaseTurn(active);
    else if (active.turnId === null && active.completed.size < 20) active.completed.add(turnId);
  });
  return backend;
}

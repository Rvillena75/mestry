// Start only inside the already paired Horus SSH profile. No OAuth/key import.
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { BridgeServer } from './bridge-server.mjs';
import { StateStore } from './store.mjs';
import { CodexBackend } from './backends/codex.mjs';
import { DriveClient } from './mestry-drive.mjs';

process.umask(0o077);
const root = '/workspace/projects/mestry-horus-smoke';
const stateDir = path.join(os.homedir(), '.local/state/mestry-s25-client');
let currentBridge = null;

async function main() {
  if (os.homedir() !== '/home/horus' || process.arch !== 'arm64') throw new Error('HORUS_PROFILE_REQUIRED');
  await fs.mkdir(stateDir, { recursive: true, mode: 0o700 });
  const directory = await fs.lstat(stateDir);
  if (!directory.isDirectory() || directory.isSymbolicLink() || (directory.mode & 0o077)) throw new Error('PRIVATE_STATE_REQUIRED');
  const tokenPath = path.join(stateDir, 'bridge-token');
  const tokenStat = await fs.lstat(tokenPath);
  if (!tokenStat.isFile() || tokenStat.isSymbolicLink() || (tokenStat.mode & 0o077)) throw new Error('PRIVATE_PAIRING_REQUIRED');
  const token = (await fs.readFile(tokenPath, 'utf8')).trim();
  if (!/^[A-Za-z0-9_-]{43,128}$/.test(token)) throw new Error('PRIVATE_PAIRING_REQUIRED');
  const codexBin = path.join(os.homedir(), '.local/bin/codex');
  await fs.access(path.join(os.homedir(), '.local/lib/node_modules/@openai/codex/bin/codex.js'));
  const backend = new CodexBackend({ codexBin, pilotProject: root,
    codexConfigs: ['approval_policy="never"', 'sandbox_mode="danger-full-access"'] });
  const bridge = new BridgeServer({ backend, store: new StateStore(path.join(stateDir, 'state.json')),
    host: '127.0.0.1', port: 8787, token, driveClient: new DriveClient(), pilotProject: root, name: 'mestry-s25-pilot', version: '0.1.0' });
  currentBridge = bridge;
  const stop = async () => { await bridge.stop(); process.exitCode = 0; };
  process.once('SIGINT', stop);
  process.once('SIGTERM', stop);
  await bridge.start();
  console.log('MESTRY_S25_BRIDGE_READY 127.0.0.1:8787 project=mestry-horus-smoke');
}

main().catch(async () => {
  console.error('MESTRY_S25_BRIDGE_FAILED_NO_SECRET_OUTPUT');
  try { await currentBridge?.stop(); } catch { /* no raw errors */ }
  process.exitCode = 1;
});

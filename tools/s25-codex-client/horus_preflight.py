#!/usr/bin/env python3
"""Read-only app-server metadata probe. No inference, listeners or raw logs."""
import json
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import threading
import time


def probe(command, project):
    version = subprocess.run(command + ["--version"], stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             timeout=8, check=True).stdout.decode().strip()
    if not re.fullmatch(r"codex-cli [0-9A-Za-z.+_-]+", version):
        raise ValueError("VERSION_NOT_RECOGNIZED")
    process = subprocess.Popen(command + ["app-server", "--listen", "stdio://"],
                               cwd=project, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, start_new_session=True)
    messages = queue.Queue(maxsize=64)
    deadline = time.monotonic() + 30

    def read_lines():
        try:
            while True:
                line = process.stdout.readline(1000001)
                if not line or len(line) > 1000000:
                    break
                messages.put(line, timeout=1)
        except Exception:
            pass

    threading.Thread(target=read_lines, daemon=True).start()

    def send(message):
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()

    def rpc(number, method, params):
        send({"id": number, "method": method, "params": params})
        while time.monotonic() < deadline:
            response = json.loads(messages.get(timeout=max(.01, deadline - time.monotonic())))
            if isinstance(response, dict) and response.get("id") == number:
                return response
        raise TimeoutError

    try:
        initialized = rpc(1, "initialize", {"clientInfo": {
            "name": "mestry_s25_preflight", "title": "MESTRY S25 Preflight", "version": "0.1.0"}})
        if "error" in initialized or "result" not in initialized:
            raise ValueError("INITIALIZE_REJECTED")
        send({"method": "initialized", "params": {}})
        account = rpc(2, "account/read", {"refreshToken": False})
        threads = rpc(3, "thread/list", {"limit": 1, "cwd": str(project)})
        config = rpc(4, "config/read", {"includeLayers": False})
        account_result = account.get("result") or {}
        account_data = account_result.get("account") or {}
        values = (config.get("result") or {}).get("config") or {}
        policy = values.get("approval_policy")
        sandbox = values.get("sandbox_mode")
        signed_in = bool(account_data)
        status = "PASS" if signed_in and "error" not in threads and "result" in threads else "INCOMPLETE"
        return {"status": status, "marker": "MESTRY_HORUS_APP_PREFLIGHT",
                "codex_version": version, "initialize_pass": True,
                "account_read_supported": "error" not in account,
                "signed_in": signed_in,
                "account_type": account_data.get("type") if account_data.get("type") in ("chatgpt", "apiKey") else "unknown",
                "project_thread_list_supported": "error" not in threads and "result" in threads,
                "approval_policy": policy if isinstance(policy, str) and policy in ("untrusted", "on-request", "on-failure", "never") else "unknown",
                "sandbox_mode": sandbox if isinstance(sandbox, str) and sandbox in ("read-only", "workspace-write", "danger-full-access") else "unknown",
                "model_turns_started": 0, "ports_opened": False, "credentials_or_conversation_content_printed": False}
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=2)
        process.stdin.close()
        process.stdout.close()


def main():
    project = Path("/workspace/projects/mestry-horus-smoke")
    entry = Path.home() / ".local/lib/node_modules/@openai/codex/bin/codex.js"
    executable = Path.home() / ".local/bin/codex"
    if str(Path.home()) != "/home/horus" or os.uname().machine != "aarch64":
        raise ValueError("RUN_INSIDE_HORUS_SSH_PROFILE")
    if not entry.is_file() or not executable.is_file() or not project.is_dir():
        raise ValueError("EXISTING_CODEX_OR_SMOKE_PROJECT_NOT_FOUND_NO_INSTALL_ATTEMPTED")
    return probe([str(executable)], project)


if __name__ == "__main__":
    try:
        result = main()
    except Exception:
        result = {"status": "ERROR", "marker": "MESTRY_HORUS_APP_PREFLIGHT",
                  "code": "PREFLIGHT_FAILED_NO_RAW_OUTPUT", "credentials_or_conversation_content_printed": False}
    print(json.dumps(result))

#!/usr/bin/env python3
"""Read one fixed smoke thread through a fresh stdio app-server; print metadata only."""
import hashlib
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import threading
import time

THREAD_ID = "01a15dae-7f34-7a22-926e-594a53f899cd"
PROJECT = "/workspace/projects/mestry-horus-smoke"
INTERRUPT_PROMPT = (
    "Prueba de detener, intento 2. No modifiques archivos. Ejecuta python3 -c "
    "'import time; time.sleep(30)' y despues responde MESTRY_INTERRUPT_2_FINISHED."
)


def read_thread():
    if str(Path.home()) != "/home/horus" or os.uname().machine != "aarch64":
        raise ValueError("RUN_INSIDE_EXISTING_HORUS_SSH_PROFILE")
    executable = Path.home() / ".local/bin/codex"
    if not executable.is_file() or not Path(PROJECT).is_dir():
        raise ValueError("EXISTING_CODEX_AND_PROJECT_REQUIRED")
    process = subprocess.Popen(
        [str(executable), "app-server", "--listen", "stdio://"], cwd=PROJECT,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, start_new_session=True,
    )
    messages = queue.Queue(maxsize=64)
    deadline = time.monotonic() + 30

    def read_lines():
        try:
            while True:
                line = process.stdout.readline(4_000_001)
                if not line or len(line) > 4_000_000:
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
                if "error" in response or "result" not in response:
                    raise ValueError("RPC_REJECTED_NO_RAW_OUTPUT")
                return response["result"]
        raise TimeoutError

    try:
        rpc(1, "initialize", {"clientInfo": {
            "name": "mestry_s25_thread_read", "title": "MESTRY read only", "version": "0.1.0",
        }})
        send({"method": "initialized", "params": {}})
        result = rpc(2, "thread/read", {"threadId": THREAD_ID, "includeTurns": True})
        thread = result.get("thread") or {}
        if thread.get("id") != THREAD_ID or thread.get("cwd") != PROJECT:
            raise ValueError("THREAD_ID_OR_PROJECT_MISMATCH")
        turns = thread.get("turns")
        if not isinstance(turns, list) or not turns:
            raise ValueError("STORED_TURNS_REQUIRED")
        summaries = []
        publication_receipts = []
        for turn in turns:
            items = turn.get("items") or []
            user_texts = [part.get("text", "") for item in items
                          if item.get("type") == "userMessage"
                          for part in item.get("content", []) if part.get("type") == "text"]
            summaries.append({
                "id": turn.get("id"), "status": turn.get("status"),
                "item_count": len(items),
                "interrupt_prompt_matches": INTERRUPT_PROMPT in user_texts,
            })
            # Read actual tool output, rather than treating assistant prose as a receipt.
            for item in items:
                if item.get("type") != "commandExecution":
                    continue
                output = item.get("aggregatedOutput") or item.get("stdout") or ""
                if not isinstance(output, str):
                    continue
                for line in output.splitlines():
                    try:
                        value = json.loads(line)
                    except (ValueError, TypeError):
                        continue
                    if isinstance(value, dict) and value.get("status") == "PUBLISHED_VERIFIED":
                        publication_receipts.append({
                            "turn_id": turn.get("id"),
                            **{key: value.get(key) for key in ("status", "revision", "file_id", "sha256")},
                        })
        last = summaries[-1]
        # Later requests must not invalidate the earlier, explicitly matched test.
        matching = [turn for turn in summaries if turn["interrupt_prompt_matches"]]
        interruption_turn = matching[-1] if matching else None
        interruption_pass = interruption_turn is not None and interruption_turn["status"] == "interrupted"
        fingerprint = hashlib.sha256(json.dumps(turns, sort_keys=True, separators=(",", ":"),
                                                ensure_ascii=False).encode()).hexdigest()
        return {"marker": "MESTRY_FRESH_THREAD_READ", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "thread_id": THREAD_ID, "same_project": True, "turn_count": len(turns),
                "last_turn": last, "interruption_turn": interruption_turn,
                "interruption": "PASS" if interruption_pass else "NOT_CONFIRMED",
                "publication_receipts_from_tool_output": publication_receipts,
                "turns_sha256": fingerprint, "model_turns_started": 0,
                "ports_opened": False, "raw_content_printed": False}
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


if __name__ == "__main__":
    try:
        outcome = read_thread()
    except Exception:
        outcome = {"marker": "MESTRY_FRESH_THREAD_READ", "status": "ERROR_NO_RAW_OUTPUT"}
    print(json.dumps(outcome, indent=2))

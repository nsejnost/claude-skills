#!/usr/bin/env python3
"""PreToolUse hook: append one JSON line per tool call to .skill-test/events.jsonl.

No-ops instantly unless a `.skill-test-scenario` marker file exists in the project
root — so ordinary sessions on this repo pay ~nothing. Never blocks a tool call:
always exits 0.
"""
import json
import os
import sys
import time

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    root = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    marker = os.path.join(root, ".skill-test-scenario")
    if not os.path.isfile(marker):
        return 0
    try:
        tool_input = json.dumps(payload.get("tool_input", {}), default=str)
        line = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": "pre_tool",
            "tool": payload.get("tool_name", "unknown"),
            "input": tool_input[:2000],
            "session_id": payload.get("session_id", ""),
        }
        outdir = os.path.join(root, ".skill-test")
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "events.jsonl"), "a") as f:
            f.write(json.dumps(line) + "\n")
    except Exception:
        pass
    return 0

if __name__ == "__main__":
    sys.exit(main())

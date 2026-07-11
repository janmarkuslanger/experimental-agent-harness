#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Minimal agent harness for Ollama: chat loop + one tool (shell)."""
import json
import subprocess
import sys
import urllib.request

MODEL = sys.argv[1] if len(sys.argv) > 1 else "llama3.2"
URL = "http://localhost:11434/api/chat"

TOOLS = [{
    "type": "function",
    "function": {
        "name": "run_shell",
        "description": "Run a shell command and return stdout+stderr.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
}]


def run_shell(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return (result.stdout + result.stderr)[:4000]


def chat(messages: list) -> dict:
    payload = json.dumps({"model": MODEL, "messages": messages, "tools": TOOLS, "stream": False}).encode()
    req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["message"]


def main():
    messages = []
    print(f"Minimal Ollama Agent ({MODEL}). Ctrl+C zum Beenden.")
    while True:
        try:
            user_input = input("> ")
        except (EOFError, KeyboardInterrupt):
            break
        messages.append({"role": "user", "content": user_input})

        while True:
            message = chat(messages)
            messages.append(message)
            tool_calls = message.get("tool_calls")
            if not tool_calls:
                print(message.get("content", ""))
                break
            for call in tool_calls:
                name = call["function"]["name"]
                args = call["function"]["arguments"]
                result = run_shell(**args) if name == "run_shell" else f"unknown tool: {name}"
                messages.append({"role": "tool", "content": result})


if __name__ == "__main__":
    main()

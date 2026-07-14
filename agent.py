#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Minimal agent harness for Ollama: chat loop + tools (shell, read_file)."""
import json
import subprocess
import sys
import urllib.request

MODEL = sys.argv[1] if len(sys.argv) > 1 else "llama3.2"
URL = "http://localhost:11434/api/chat"

TOOLS = [
    {
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
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file and return its content.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
]


def run_shell(command: str) -> str:
    """Execute a shell command and return its combined output.

    Args:
        command: Shell command to execute (passed to the system shell).

    Returns:
        Combined stdout and stderr, truncated to 4000 characters.
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return (result.stdout + result.stderr)[:4000]


def read_file(path: str) -> str:
    """Read a text file and return its content.

    Args:
        path: Path to the file to read.

    Returns:
        File content, truncated to 4000 characters, or an error message
        if the file cannot be read.
    """
    try:
        with open(path, "r", errors="replace") as f:
            return f.read()[:4000]
    except OSError as e:
        return f"error: {e}"


def chat(messages: list) -> dict:
    """Send the conversation to Ollama and return the assistant's reply.

    Args:
        messages: Full conversation history in Ollama chat format
            (list of dicts with "role" and "content", plus any prior
            "tool" results).

    Returns:
        The "message" object from Ollama's response, which may contain
        "content" and/or "tool_calls".
    """
    payload = json.dumps({"model": MODEL, "messages": messages, "tools": TOOLS, "stream": False}).encode()
    req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["message"]


TOOL_FUNCS = {"run_shell": run_shell, "read_file": read_file}


def main():
    """Run the interactive chat loop, dispatching tool calls until the model replies with plain text."""
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
                func = TOOL_FUNCS.get(name)
                result = func(**args) if func else f"unknown tool: {name}"
                messages.append({"role": "tool", "content": result})


if __name__ == "__main__":
    main()

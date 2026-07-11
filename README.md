# experimental-agent-harness

Minimal agent harness for [Ollama](https://ollama.com) — a single Python file, no dependencies, run with `uv`.

## Requirements

- [uv](https://docs.astral.sh/uv/) installed
- Ollama running locally (`ollama serve`), model pulled (e.g. `ollama pull llama3.2`)

## Usage

```bash
uv run agent.py             # uses model "llama3.2"
uv run agent.py mistral      # different model
```

The agent runs a chat loop against Ollama and has two tools:

- `run_shell` — execute a shell command
- `read_file` — read a text file's content

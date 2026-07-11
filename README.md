# experimental-agent-harness

Minimalistischer Agent-Harness für [Ollama](https://ollama.com) — eine einzige Python-Datei, keine Dependencies, gestartet mit `uv`.

## Voraussetzungen

- [uv](https://docs.astral.sh/uv/) installiert
- Ollama läuft lokal (`ollama serve`), Modell gezogen (z. B. `ollama pull llama3.2`)

## Nutzung

```bash
uv run agent.py             # nutzt Modell "llama3.2"
uv run agent.py mistral      # anderes Modell
```

Der Agent führt eine Chat-Schleife mit Ollama und hat ein Tool (`run_shell`), mit dem das Modell Shell-Befehle ausführen kann.

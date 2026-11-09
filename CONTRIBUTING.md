# Contributing to AgentRace

Thanks for helping make coding-agent comparisons more reproducible.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Good first contributions

- Add an adapter for another local coding agent.
- Improve cross-platform Git worktree handling.
- Add parsers for test frameworks so AgentRace can score partial test passes.
- Improve report export while keeping results local-first.

Please keep adapters explicit, auditable, and configurable. Avoid adding hidden network calls or telemetry.

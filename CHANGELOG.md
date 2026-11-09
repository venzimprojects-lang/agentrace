# Changelog

## 0.1.0 — 2026-11-09

Initial public alpha.

### Added

- Claude Code, Codex and Gemini CLI adapters.
- Isolated detached Git worktrees per agent.
- Parallel agent execution.
- User-defined validation checks.
- Deterministic local scoring.
- `doctor`, `run`, `results`, `report` and `demo` CLI commands.
- Standalone HTML reports.
- Linux, macOS and Windows CI on Python 3.11 and 3.12.
- Windows console fallback for non-UTF-8 terminals.
- MIT license, contribution guide, security notes and issue templates.

### Known limitations

- No partial test-result parsing yet.
- Cost/token metadata is not normalized across agents yet.
- Agent CLIs can change flags and output formats between releases.
- Git worktrees are isolation, not a security sandbox.

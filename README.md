<div align="center">

# 🏁 AgentRace

### Race Claude Code, Codex and Gemini CLI on **your own codebase**.

**Stop arguing which coding agent is better. Give them the same task, run the same checks, and compare the result.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

</div>

---

## Why AgentRace?

Generic leaderboards cannot tell you which agent works best on *your* repository, conventions, tests and stack.
AgentRace gives supported coding agents the same task in isolated Git worktrees, runs the same validation commands, and produces one local report.

```text
                        ┌────────────────────┐
                        │     YOUR REPO      │
                        │    committed HEAD  │
                        └─────────┬──────────┘
                                  │
                 isolated Git worktrees
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
          ┌────────────┐    ┌────────────┐   ┌────────────┐
          │ Claude Code│    │   Codex    │   │ Gemini CLI │
          └─────┬──────┘    └─────┬──────┘   └─────┬──────┘
                │                 │                │
                └─────────────────┼────────────────┘
                                  ▼
                         same validation checks
                                  │
                                  ▼
                       score + HTML race report
```

## Example result

```text
                    🏁 AgentRace Results
┏━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┓
┃ Agent       ┃ Score ┃ Checks ┃ Time   ┃ Files ┃ Diff      ┃
┡━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━┩
│ Codex       │ 100.0 │  1/1   │  92.0s │     4 │ +87/-18   │
│ Claude Code │  98.3 │  1/1   │ 111.0s │     6 │ +121/-26  │
│ Gemini CLI  │  36.8 │  0/1   │ 136.0s │     8 │ +169/-34  │
└─────────────┴───────┴────────┴────────┴───────┴───────────┘

🏆 Winner: Codex
```

> The numbers above are demo data, not a claim about global model quality.

## Quick start

### 1. Install AgentRace

For the first public release, clone the repository and install it locally:

```bash
git clone https://github.com/venzimprojects-lang/agentrace.git
cd agentrace
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Check your agents

```bash
agentrace doctor
```

AgentRace currently detects:

- Claude Code (`claude`)
- OpenAI Codex CLI (`codex`)
- Google Gemini CLI (`gemini`)

### 3. Race them

From a Git repository with a clean committed `HEAD`:

```bash
agentrace run   "Add rate limiting to the FastAPI API"   --check "pytest -q"
```

Add more checks by repeating `--check`:

```bash
agentrace run   "Refactor the auth service without changing behavior"   -c "pytest -q"   -c "ruff check ."   -c "mypy src"
```

### 4. Generate a shareable local report

```bash
agentrace report -o result.html
```

No AgentRace account is required. Results stay on your machine.

## Try it without any AI agents

```bash
agentrace demo
```

This renders a demo race and creates `agentrace-demo.html` so you can preview the output immediately.

## How scoring works in v0.1

AgentRace intentionally uses a simple, inspectable formula instead of another LLM judge:

- **25 points** — agent process completed successfully
- **60 points** — configured validation checks, split equally across checks
- **10 points** — relative execution speed among successful agents
- **5 points** — agent was available and runnable

If you provide no validation checks, AgentRace reduces the available quality score. That is deliberate: speed alone is not a useful coding benchmark.

## Fairness rules

AgentRace tries to make a local comparison reproducible:

1. Every agent starts from the exact same Git commit.
2. Every agent gets its own detached Git worktree.
3. Every agent receives the same task text and benchmark rules.
4. The same user-defined validation commands run after each agent.
5. Agents do not read each other's worktrees or results through AgentRace.

This does **not** make scores scientifically universal. Models, subscriptions, local configuration, tools, network access and agent permissions can all affect results.

## Safety

Coding agents can execute commands. AgentRace isolates repository copies with Git worktrees, but that is **not a security sandbox**.

Do not run untrusted code or agents on a machine containing sensitive credentials. Review each agent's own sandbox and permission settings. See [SECURITY.md](SECURITY.md).

## Supported agent commands

AgentRace currently uses safe-ish automation modes intended to let the agent edit its isolated workspace while preserving its own permission system:

- Claude Code: headless print mode with edit permissions
- Codex: non-interactive `exec` in a `workspace-write` sandbox with approval prompts disabled
- Gemini CLI: headless prompt mode with `auto_edit`

CLI interfaces evolve. Adapter commands are intentionally small and isolated so they can be updated quickly.

## Roadmap

- [x] CLI doctor
- [x] Claude / Codex / Gemini adapters
- [x] Isolated Git worktrees
- [x] Parallel racing
- [x] User-defined checks
- [x] Deterministic scoring
- [x] Standalone HTML report
- [ ] Partial test-result parsing (pytest, Vitest/Jest, Go test)
- [ ] Cost / token capture where agents expose it reliably
- [ ] Reusable benchmark suites
- [ ] SVG / PNG share cards
- [ ] More adapters
- [ ] GitHub Action mode

## Philosophy

AgentRace does not try to answer:

> Which AI coding agent is best?

It asks a more useful question:

> **Which coding agent performs best on this task, in this repository, with these checks?**

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT

# Benchmark methodology

AgentRace is a **local comparison harness**, not a universal model leaderboard.

Its goal is to make one head-to-head comparison more repeatable by controlling the parts it can control.

## What AgentRace controls

For every race:

1. Each agent starts from the same committed Git `HEAD`.
2. Each agent gets a separate detached Git worktree.
3. Each agent receives the same task text.
4. The same validation commands are executed after the agent finishes.
5. AgentRace calculates score from process completion, checks and relative speed.

## What AgentRace does not control

Results can still be affected by:

- model or CLI version;
- subscription tier and rate limits;
- local agent configuration;
- enabled MCP servers, skills or tools;
- network availability;
- provider-side model routing;
- operating system and hardware;
- repository-specific instructions;
- nondeterminism in the models themselves.

Because of this, AgentRace should not be used to make claims such as "Model X is universally better than Model Y" from one run.

## v0.1 scoring

The current score is intentionally transparent:

- 5 points: adapter is available and runnable;
- 25 points: agent process exits successfully;
- 60 points: validation checks, split equally across checks;
- 10 points: relative speed among successful agents.

A run without user-defined validation checks receives substantially less quality credit.

## Why not use an LLM judge?

LLM judges can be useful, but they add another model and another prompt whose behavior can vary over time.

For v0.1, AgentRace prefers deterministic signals that a user can inspect directly.

Future versions may support optional pluggable judges, but they should be clearly separated from the core score.

## Recommended usage

Good benchmark tasks have:

- one clear requested change;
- deterministic tests or checks;
- a clean committed baseline;
- enough scope to expose differences between agents;
- no secrets in prompts or repository files.

Whenever possible, run the same benchmark more than once before drawing conclusions.

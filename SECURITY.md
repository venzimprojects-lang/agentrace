# Security

AgentRace launches third-party coding agents and user-defined validation commands on your machine.
Those tools can execute code and modify files inside isolated Git worktrees.

- Review the permissions and sandbox settings of each installed agent.
- Do not benchmark untrusted repositories without an external sandbox.
- Do not include secrets in benchmark prompts.
- Validation commands passed with `--check` are executed by your shell.

To report a security issue, open a private GitHub security advisory once the repository is published.

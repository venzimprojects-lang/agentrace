from __future__ import annotations

from datetime import datetime, timezone

from .models import AgentResult, CheckResult, RaceResult


def demo_result() -> RaceResult:
    def check(agent: str, passed: bool, seconds: float) -> CheckResult:
        return CheckResult(
            name="pytest",
            command="pytest -q",
            exit_code=0 if passed else 1,
            duration_seconds=seconds,
            output_tail=f"demo check for {agent}",
        )

    agents = [
        AgentResult("Codex", ["codex", "exec"], True, True, 0, 92.0, 4, 87, 18, [check("Codex", True, 2.2)], 100.0),
        AgentResult("Claude Code", ["claude", "-p"], True, True, 0, 111.0, 6, 121, 26, [check("Claude", True, 2.1)], 98.3),
        AgentResult("Gemini CLI", ["gemini", "-p"], True, True, 0, 136.0, 8, 169, 34, [check("Gemini", False, 2.0)], 36.8),
    ]
    return RaceResult(
        task="Add rate limiting to a FastAPI endpoint",
        repository="demo/sample-fastapi-app",
        base_commit="demo000000000000000000000000000000000000",
        created_at=datetime.now(timezone.utc).isoformat(),
        agents=agents,
        winner="Codex",
    )

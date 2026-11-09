from __future__ import annotations

from .models import AgentResult


def score_results(results: list[AgentResult]) -> None:
    completed_times = [r.duration_seconds for r in results if r.completed and r.exit_code == 0]
    fastest = min(completed_times) if completed_times else None

    for result in results:
        score = 0.0
        if result.available:
            score += 5
        if result.completed and result.exit_code == 0:
            score += 25

        if result.checks:
            passed = sum(1 for c in result.checks if c.passed)
            score += 60 * (passed / len(result.checks))
        elif result.completed and result.exit_code == 0:
            # A race without checks is useful for orchestration, but not a strong benchmark.
            score += 20

        if fastest is not None and result.completed and result.exit_code == 0:
            ratio = fastest / max(result.duration_seconds, fastest)
            score += 10 * ratio

        result.score = round(min(score, 100.0), 1)


def pick_winner(results: list[AgentResult]) -> str | None:
    eligible = [r for r in results if r.available and r.completed]
    if not eligible:
        return None
    return max(eligible, key=lambda r: (r.score, -r.duration_seconds)).agent

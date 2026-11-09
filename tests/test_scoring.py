from agentrace.models import AgentResult, CheckResult
from agentrace.scoring import pick_winner, score_results


def test_passing_agent_beats_failing_agent():
    passing = AgentResult(
        agent="A", command=[], available=True, completed=True, exit_code=0, duration_seconds=10,
        checks=[CheckResult("tests", "pytest", 0, 1.0)],
    )
    failing = AgentResult(
        agent="B", command=[], available=True, completed=True, exit_code=0, duration_seconds=5,
        checks=[CheckResult("tests", "pytest", 1, 1.0)],
    )
    score_results([passing, failing])
    assert passing.score > failing.score
    assert pick_winner([passing, failing]) == "A"

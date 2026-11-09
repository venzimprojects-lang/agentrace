from agentrace.demo import demo_result
from agentrace.report import render_html


def test_report_contains_winner_and_task():
    html = render_html(demo_result())
    assert "AgentRace" in html
    assert "Codex" in html
    assert "rate limiting" in html

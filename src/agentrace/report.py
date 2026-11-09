from __future__ import annotations

import html
from pathlib import Path

from .models import RaceResult


def render_html(result: RaceResult) -> str:
    rows = []
    for r in sorted(result.agents, key=lambda x: x.score, reverse=True):
        checks = f"{sum(c.passed for c in r.checks)}/{len(r.checks)}" if r.checks else "—"
        rows.append(
            "<tr>"
            f"<td>{html.escape(r.agent)}</td>"
            f"<td><strong>{r.score:.1f}</strong></td>"
            f"<td>{checks}</td>"
            f"<td>{r.duration_seconds:.1f}s</td>"
            f"<td>{r.files_changed}</td>"
            f"<td>+{r.insertions}/-{r.deletions}</td>"
            "</tr>"
        )
    winner = html.escape(result.winner or "No winner")
    task = html.escape(result.task)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgentRace result</title>
<style>
body{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;background:#0b1020;color:#eef2ff;margin:0;padding:48px 20px}}
.card{{max-width:900px;margin:auto;background:#111833;border:1px solid #263158;border-radius:22px;padding:30px;box-shadow:0 20px 70px #0007}}
.eyebrow{{color:#9fb0ff;font-size:13px;font-weight:800;letter-spacing:.14em;text-transform:uppercase}}
h1{{font-size:44px;margin:8px 0 6px}} .task{{color:#c7d2fe;font-size:18px}} .winner{{margin:28px 0;padding:18px 20px;border-radius:15px;background:#17224a;font-size:24px}}
table{{width:100%;border-collapse:collapse;margin-top:22px}} th,td{{padding:14px 10px;border-bottom:1px solid #263158;text-align:left}} th{{color:#9fb0ff;font-size:12px;text-transform:uppercase;letter-spacing:.08em}}
small{{display:block;color:#7f8bb5;margin-top:24px}} @media(max-width:700px){{h1{{font-size:34px}} .card{{padding:20px}} table{{font-size:13px}}}}
</style></head><body><main class="card"><div class="eyebrow">AI coding agent benchmark</div><h1>🏁 AgentRace</h1>
<div class="task">{task}</div><div class="winner">🏆 Winner: <strong>{winner}</strong></div>
<table><thead><tr><th>Agent</th><th>Score</th><th>Checks</th><th>Time</th><th>Files</th><th>Diff</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<small>Generated locally by AgentRace. Scores combine agent completion, configured checks, and relative execution time.</small></main></body></html>"""


def write_report(result: RaceResult, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_html(result), encoding="utf-8")
    return destination

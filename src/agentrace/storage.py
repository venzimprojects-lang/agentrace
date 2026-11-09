from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import AgentResult, CheckResult, RaceResult


def save_result(repo: Path, result: RaceResult) -> Path:
    root = RaceResult.results_path(repo)
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = root / f"race-{stamp}.json"
    result.results_dir = str(path.parent)
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    (root / "latest.json").write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return path


def load_result(path: Path) -> RaceResult:
    data = json.loads(path.read_text(encoding="utf-8"))
    agents: list[AgentResult] = []
    for item in data["agents"]:
        checks = [CheckResult(**c) for c in item.pop("checks", [])]
        agents.append(AgentResult(checks=checks, **item))
    return RaceResult(agents=agents, **{k: v for k, v in data.items() if k != "agents"})


def latest_result(repo: Path) -> Path:
    path = RaceResult.results_path(repo) / "latest.json"
    if not path.exists():
        raise FileNotFoundError("No AgentRace results yet. Run `agentrace run ...` or `agentrace demo`.")
    return path

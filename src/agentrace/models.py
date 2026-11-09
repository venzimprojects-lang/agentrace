from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CheckResult:
    name: str
    command: str
    exit_code: int
    duration_seconds: float
    output_tail: str = ""

    @property
    def passed(self) -> bool:
        return self.exit_code == 0


@dataclass(slots=True)
class AgentResult:
    agent: str
    command: list[str]
    available: bool
    completed: bool
    exit_code: int | None
    duration_seconds: float
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    checks: list[CheckResult] = field(default_factory=list)
    score: float = 0.0
    error: str | None = None
    stdout_tail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RaceResult:
    task: str
    repository: str
    base_commit: str
    created_at: str
    agents: list[AgentResult]
    winner: str | None = None
    results_dir: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def results_path(cls, root: Path) -> Path:
        return root / ".agentrace" / "results"

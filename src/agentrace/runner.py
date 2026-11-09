from __future__ import annotations

import concurrent.futures
import os
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from .adapters import AgentAdapter
from .gitops import add_worktree, diff_stats, head_commit, remove_worktree, slugify
from .models import AgentResult, CheckResult, RaceResult
from .scoring import pick_winner, score_results


PROMPT_TEMPLATE = """You are competing in AgentRace, a coding-agent benchmark.

Task:
{task}

Rules:
- Work only inside this repository checkout.
- Implement the requested change completely.
- Do not change the task or benchmark configuration.
- Avoid destructive commands and do not access secrets.
- Keep the solution focused; do not create unrelated files.
- When finished, leave all code changes in the working tree.
"""


def _tail(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def _run_check(worktree: Path, command: str, timeout: int) -> CheckResult:
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=worktree,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=os.environ.copy(),
    )
    duration = time.perf_counter() - started
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return CheckResult(
        name=command,
        command=command,
        exit_code=proc.returncode,
        duration_seconds=round(duration, 3),
        output_tail=_tail(output),
    )


def _run_agent(
    repo: Path,
    base_commit: str,
    adapter: AgentAdapter,
    task: str,
    checks: list[str],
    timeout: int,
    check_timeout: int,
    workspace_root: Path,
) -> AgentResult:
    if not adapter.available():
        return AgentResult(
            agent=adapter.name,
            command=adapter.command("<task>"),
            available=False,
            completed=False,
            exit_code=None,
            duration_seconds=0.0,
            error=f"{adapter.binary} not found on PATH",
        )

    worktree = workspace_root / slugify(adapter.name)
    add_worktree(repo, worktree, base_commit)
    prompt = PROMPT_TEMPLATE.format(task=task)
    command = adapter.command(prompt)
    started = time.perf_counter()

    try:
        proc = subprocess.run(
            command,
            cwd=worktree,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
        duration = time.perf_counter() - started
        files, insertions, deletions = diff_stats(worktree)
        check_results = [_run_check(worktree, c, check_timeout) for c in checks]
        combined = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return AgentResult(
            agent=adapter.name,
            command=command,
            available=True,
            completed=True,
            exit_code=proc.returncode,
            duration_seconds=round(duration, 3),
            files_changed=files,
            insertions=insertions,
            deletions=deletions,
            checks=check_results,
            stdout_tail=_tail(combined),
            error=None if proc.returncode == 0 else f"agent exited with code {proc.returncode}",
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - started
        files, insertions, deletions = diff_stats(worktree)
        return AgentResult(
            agent=adapter.name,
            command=command,
            available=True,
            completed=False,
            exit_code=None,
            duration_seconds=round(duration, 3),
            files_changed=files,
            insertions=insertions,
            deletions=deletions,
            error=f"timed out after {timeout}s",
            stdout_tail=_tail((exc.stdout or "") if isinstance(exc.stdout, str) else ""),
        )
    except Exception as exc:  # noqa: BLE001 - convert agent failures into benchmark results
        duration = time.perf_counter() - started
        return AgentResult(
            agent=adapter.name,
            command=command,
            available=True,
            completed=False,
            exit_code=None,
            duration_seconds=round(duration, 3),
            error=str(exc),
        )
    finally:
        remove_worktree(repo, worktree)


def run_race(
    repo: Path,
    task: str,
    adapters: list[AgentAdapter],
    checks: list[str],
    timeout: int = 900,
    check_timeout: int = 300,
    parallel: bool = True,
) -> RaceResult:
    base = head_commit(repo)
    created = datetime.now(timezone.utc).isoformat()

    with tempfile.TemporaryDirectory(prefix="agentrace-") as temp:
        root = Path(temp)
        if parallel:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(adapters)) as pool:
                futures = [
                    pool.submit(
                        _run_agent,
                        repo,
                        base,
                        adapter,
                        task,
                        checks,
                        timeout,
                        check_timeout,
                        root,
                    )
                    for adapter in adapters
                ]
                results = [f.result() for f in futures]
        else:
            results = [
                _run_agent(
                    repo,
                    base,
                    adapter,
                    task,
                    checks,
                    timeout,
                    check_timeout,
                    root,
                )
                for adapter in adapters
            ]

    score_results(results)
    winner = pick_winner(results)
    return RaceResult(
        task=task,
        repository=str(repo.resolve()),
        base_commit=base,
        created_at=created,
        agents=results,
        winner=winner,
    )

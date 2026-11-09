from __future__ import annotations

import re
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise GitError(proc.stderr.strip() or proc.stdout.strip() or "git command failed")
    return proc


def ensure_repository(repo: Path) -> None:
    proc = run_git(repo, "rev-parse", "--is-inside-work-tree", check=False)
    if proc.returncode != 0 or proc.stdout.strip() != "true":
        raise GitError(f"{repo} is not a Git repository")


def head_commit(repo: Path) -> str:
    return run_git(repo, "rev-parse", "HEAD").stdout.strip()


def is_dirty(repo: Path) -> bool:
    return bool(run_git(repo, "status", "--porcelain").stdout.strip())


def add_worktree(repo: Path, destination: Path, commit: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run_git(repo, "worktree", "add", "--detach", str(destination), commit)


def remove_worktree(repo: Path, destination: Path) -> None:
    run_git(repo, "worktree", "remove", "--force", str(destination), check=False)
    run_git(repo, "worktree", "prune", check=False)


def diff_stats(worktree: Path) -> tuple[int, int, int]:
    proc = run_git(worktree, "diff", "--numstat", "HEAD", check=False)
    files = insertions = deletions = 0
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        files += 1
        if parts[0].isdigit():
            insertions += int(parts[0])
        if parts[1].isdigit():
            deletions += int(parts[1])

    # Include untracked files, which git diff does not count.
    untracked = run_git(worktree, "ls-files", "--others", "--exclude-standard", check=False)
    for rel in [x.strip() for x in untracked.stdout.splitlines() if x.strip()]:
        files += 1
        path = worktree / rel
        if path.is_file():
            try:
                insertions += len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
            except OSError:
                pass
    return files, insertions, deletions


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "agent"

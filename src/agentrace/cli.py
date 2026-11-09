from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .adapters import default_adapters
from .demo import demo_result
from .gitops import GitError, ensure_repository, is_dirty
from .report import write_report
from .runner import run_race
from .storage import latest_result, load_result, save_result

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Race AI coding agents on your code.")
console = Console()


def _supports_unicode() -> bool:
    encoding = (console.encoding or "").lower().replace("-", "")
    return encoding in {"utf8", "utf_8"}


def _show(result) -> None:
    unicode_ok = _supports_unicode()
    table = Table(
        title="🏁 AgentRace Results" if unicode_ok else "AgentRace Results",
        box=box.ROUNDED if unicode_ok else box.ASCII,
    )
    table.add_column("Agent", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Checks", justify="center")
    table.add_column("Time", justify="right")
    table.add_column("Files", justify="right")
    table.add_column("Diff", justify="right")
    table.add_column("Status")
    for r in sorted(result.agents, key=lambda x: x.score, reverse=True):
        checks = f"{sum(c.passed for c in r.checks)}/{len(r.checks)}" if r.checks else "-"
        status = ("✓" if unicode_ok else "OK") if r.completed and r.exit_code == 0 else (r.error or "failed")
        table.add_row(
            r.agent,
            f"{r.score:.1f}",
            checks,
            f"{r.duration_seconds:.1f}s",
            str(r.files_changed),
            f"+{r.insertions}/-{r.deletions}",
            status,
        )
    console.print(table)
    if result.winner:
        winner_label = "🏆 Winner" if unicode_ok else "Winner"
        console.print(
            Panel.fit(
                f"{winner_label}: [bold]{result.winner}[/bold]",
                border_style="green",
                box=box.ROUNDED if unicode_ok else box.ASCII,
            )
        )


@app.command()
def doctor() -> None:
    """Check which supported coding agents are installed."""
    table = Table(title="AgentRace Doctor")
    table.add_column("Agent")
    table.add_column("Status")
    table.add_column("Version")
    for adapter in default_adapters():
        if not adapter.available():
            table.add_row(adapter.name, "[red]not found[/red]", "—")
            continue
        try:
            proc = subprocess.run(
                adapter.version_command(),
                check=False,
                text=True,
                capture_output=True,
                timeout=10,
            )
            version = ((proc.stdout or proc.stderr) or "installed").strip().splitlines()[0][:100]
        except Exception:  # noqa: BLE001
            version = "installed"
        table.add_row(adapter.name, "[green]ready[/green]", version)
    console.print(table)


@app.command("run")
def run_command(
    task: Annotated[str, typer.Argument(help="The exact coding task given to every agent.")],
    repo: Annotated[Path, typer.Option("--repo", "-r", help="Git repository to benchmark.")] = Path("."),
    check: Annotated[
        list[str] | None,
        typer.Option("--check", "-c", help="Validation command. Repeat for multiple checks."),
    ] = None,
    timeout: Annotated[int, typer.Option(help="Per-agent timeout in seconds.")] = 900,
    check_timeout: Annotated[int, typer.Option(help="Per-check timeout in seconds.")] = 300,
    sequential: Annotated[
        bool,
        typer.Option(help="Run agents one-by-one instead of in parallel."),
    ] = False,
    allow_dirty: Annotated[
        bool,
        typer.Option(help="Allow a repository with uncommitted changes; race still starts from HEAD."),
    ] = False,
) -> None:
    """Run the same task against every available supported agent."""
    repo = repo.resolve()
    checks = check or []
    try:
        ensure_repository(repo)
        if is_dirty(repo) and not allow_dirty:
            raise typer.BadParameter(
                "Repository has uncommitted changes. Commit/stash them, or pass --allow-dirty. "
                "AgentRace always benchmarks the committed HEAD."
            )
    except GitError as exc:
        raise typer.BadParameter(str(exc)) from exc

    adapters = default_adapters()
    if not any(a.available() for a in adapters):
        console.print("[red]No supported agents found.[/red] Run `agentrace doctor`.")
        raise typer.Exit(2)

    console.print(f"[bold]Task:[/bold] {task}")
    console.print(f"[bold]Repository:[/bold] {repo}")
    console.print("Running each agent in an isolated Git worktree...")
    result = run_race(
        repo=repo,
        task=task,
        adapters=adapters,
        checks=checks,
        timeout=timeout,
        check_timeout=check_timeout,
        parallel=not sequential,
    )
    path = save_result(repo, result)
    report_path = write_report(result, path.with_suffix(".html"))
    _show(result)
    console.print(f"Result: [cyan]{path}[/cyan]")
    console.print(f"HTML report: [cyan]{report_path}[/cyan]")


@app.command()
def results(
    repo: Annotated[Path, typer.Option("--repo", "-r")] = Path("."),
    json_output: Annotated[bool, typer.Option("--json", help="Print raw JSON.")] = False,
) -> None:
    """Show the most recent race result."""
    path = latest_result(repo.resolve())
    result = load_result(path)
    if json_output:
        console.print_json(json.dumps(result.to_dict()))
    else:
        _show(result)


@app.command()
def report(
    repo: Annotated[Path, typer.Option("--repo", "-r")] = Path("."),
    output: Annotated[Path, typer.Option("--output", "-o")] = Path("agentrace-report.html"),
) -> None:
    """Generate a standalone shareable HTML report from the latest result."""
    result = load_result(latest_result(repo.resolve()))
    path = write_report(result, output.resolve())
    console.print(f"Wrote [cyan]{path}[/cyan]")


@app.command()
def demo(
    output: Annotated[Path, typer.Option("--output", "-o")] = Path("agentrace-demo.html"),
) -> None:
    """Preview AgentRace without installing any AI coding agents."""
    result = demo_result()
    _show(result)
    path = write_report(result, output.resolve())
    console.print(f"Demo report: [cyan]{path}[/cyan]")


if __name__ == "__main__":
    app()

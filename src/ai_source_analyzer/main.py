from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ai_source_analyzer.core.provider_loader import load_providers
from ai_source_analyzer.core.providers_registry import ProvidersRegistry
from ai_source_analyzer.core.runner import QueryRunner
from ai_source_analyzer.report import CliReporter, JsonReporter, ReportData

app = typer.Typer(add_completion=False)
console = Console()


def warn(message: str) -> None:
    console.print(f"[yellow]Warning:[/yellow] {message}")


def build_registry() -> ProvidersRegistry:
    registry = ProvidersRegistry()
    load_providers(registry=registry)
    return registry


def read_queries(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    content = path.read_text(encoding="utf-8")

    queries = [line.strip() for line in content.splitlines() if line.strip()]

    if not queries:
        raise ValueError("No queries found in file")

    return queries


def select_providers(registry: ProvidersRegistry, provider_names: list[str] | None):
    if provider_names:
        return registry.get_many(provider_names)

    return registry.all()


@app.command()
def main(
    path: str = typer.Option(
        ...,
        "--path",
        "-p",
        help="Path to TXT file with queries",
    ),
    provider: list[str] | None = typer.Option(
        None,
        "--provider",
        "-pr",
        help="Provider name (can be used multiple times)",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Save result JSON to file",
    ),
):
    registry = build_registry()
    runner = QueryRunner()

    try:
        queries = read_queries(Path(path))
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)

    try:
        providers = select_providers(registry, provider)
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)

    if not providers:
        console.print("[red]No available providers[/red]")
        raise typer.Exit(1)

    responses = runner.run_many(
        providers=providers,
        queries=queries,
    )
    report_data = ReportData(
        queries=queries,
        providers=[p.name for p in providers],
        responses=responses,
    )

    if output is None:
        CliReporter(console=console).write(report_data)
        return

    out_path = Path(output)
    JsonReporter().write(report_data, out_path)

    console.print(f"[bold green]Saved JSON:[/bold green] {out_path}")


if __name__ == "__main__":
    app()

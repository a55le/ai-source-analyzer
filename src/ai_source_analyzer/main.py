from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ai_source_analyzer.application.dto.report_data import ReportData
from ai_source_analyzer.application.use_cases.run_queries import RunQueriesUseCase
from ai_source_analyzer.infrastructure.config.settings import settings
from ai_source_analyzer.infrastructure.io.query_file_reader import QueryFileReader
from ai_source_analyzer.infrastructure.logging.logger import logger
from ai_source_analyzer.infrastructure.providers.provider_loader import load_providers
from ai_source_analyzer.infrastructure.providers.providers_registry import (
    ProvidersRegistry,
)
from ai_source_analyzer.infrastructure.reporters.cli_reporter import CliReporter
from ai_source_analyzer.infrastructure.reporters.json_reporter import JsonReporter

app = typer.Typer(add_completion=False)
console = Console()


def build_registry() -> ProvidersRegistry:
    registry = ProvidersRegistry()
    load_providers(
        registry=registry,
        settings=settings,
        logger=logger,
    )
    return registry


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
    query_reader = QueryFileReader()
    run_queries = RunQueriesUseCase()

    try:
        queries = query_reader.read(Path(path))
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

    responses = run_queries.execute(
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

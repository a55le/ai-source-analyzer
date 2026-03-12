from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from ai_source_analyzer.application.dto.analysis_data import AnalysisData
from ai_source_analyzer.application.ports.reporter import ReporterPort
from ai_source_analyzer.application.use_cases.run_queries import RunQueriesUseCase
from ai_source_analyzer.infrastructure.config.settings import settings
from ai_source_analyzer.infrastructure.io.query_file_reader import QueryFileReader
from ai_source_analyzer.infrastructure.logging.logger import logger
from ai_source_analyzer.infrastructure.providers.provider_loader import load_providers
from ai_source_analyzer.infrastructure.providers.providers_registry import (
    ProvidersRegistry,
)
from ai_source_analyzer.infrastructure.reporters import getReporter

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

    total_requests = len(providers) * len(queries)
    with Progress(
        SpinnerColumn(),
        TextColumn("Отправка запросов"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task("requests", total=total_requests)

        def on_progress(
            _provider_name: str,
            _query: str,
            completed: int,
            _total: int,
        ) -> None:
            progress.update(
                task_id,
                completed=completed,
            )

        responses = run_queries.execute(
            providers=providers,
            queries=queries,
            on_progress=on_progress,
        )

    report_data = AnalysisData(
        queries=queries,
        providers=[p.name for p in providers],
        responses=responses,
    )

    ext = output.split(".")[-1] if output else "cli"
    reporter: ReporterPort = getReporter(ext)

    reporter.write(
        data=report_data, output_path=Path(output) if output is not None else None
    )


if __name__ == "__main__":
    app()

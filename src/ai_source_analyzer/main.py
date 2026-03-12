from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_source_analyzer.core.domains_stats_aggregator import get_domains_stats
from ai_source_analyzer.core.provider_loader import load_providers
from ai_source_analyzer.core.providers_registry import ProvidersRegistry
from ai_source_analyzer.core.runner import QueryRunner

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

    queries = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    if not queries:
        raise ValueError("No queries found in file")

    return queries


def select_providers(registry: ProvidersRegistry, provider_names: list[str] | None):
    if provider_names:
        return registry.get_many(provider_names)

    return registry.all()


def print_domain_stats(stats: dict[str, int]) -> None:
    table = Table(title="Site Mentions")

    table.add_column("Site", style="cyan")
    table.add_column("Mentions", justify="right")

    for domain, count in stats.items():
        table.add_row(domain, str(count))

    console.print(table)


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

    domain_stats = get_domains_stats(responses)

    if output is None:
        print_domain_stats(domain_stats)
        return

    payload = {
        "queries": queries,
        "providers": [p.name for p in providers],
        "site_mentions": domain_stats,
        "responses": [
            r.model_dump(mode="json", exclude_none=True)
            for r in responses
        ],
    }

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    console.print(f"[bold green]Saved JSON:[/bold green] {out_path}")


if __name__ == "__main__":
    app()
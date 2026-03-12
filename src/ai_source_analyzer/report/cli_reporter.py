from pathlib import Path

from rich.console import Console
from rich.table import Table

from ai_source_analyzer.core.domains_stats_aggregator import get_domains_stats
from ai_source_analyzer.report.base import BaseReporter, ReportData


class CliReporter(BaseReporter):
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def write(self, data: ReportData, output_path: Path | None = None) -> None:
        stats = get_domains_stats(data.responses)
        table = Table(title="Site Mentions")
        table.add_column("Site", style="cyan")
        table.add_column("Mentions", justify="right")

        for domain, count in stats.items():
            table.add_row(domain, str(count))

        self._console.print(table)

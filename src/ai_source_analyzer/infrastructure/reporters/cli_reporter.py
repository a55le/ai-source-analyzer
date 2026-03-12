from pathlib import Path

from rich.console import Console
from rich.table import Table

from ai_source_analyzer.application.dto.analysis_data import AnalysisData
from ai_source_analyzer.application.ports.reporter import ReporterPort
from ai_source_analyzer.domain.services.build_domain_report import get_domains_stats


class CliReporter(ReporterPort):
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def write(self, data: AnalysisData, output_path: Path | None = None) -> None:
        stats = get_domains_stats(data.responses)
        table = Table(title="Site Mentions")
        table.add_column("Site", style="cyan")
        table.add_column("Mentions", justify="right")

        for domain, count in stats.items():
            table.add_row(domain, str(count))

        self._console.print(table)

import json
from pathlib import Path

from ai_source_analyzer.core.domains_stats_aggregator import build_domain_report
from ai_source_analyzer.report.base import BaseReporter, ReportData


class JsonReporter(BaseReporter):
    def write(self, data: ReportData, output_path: Path | None = None) -> None:
        if output_path is None:
            raise ValueError("Output path is required for JSON reporter")

        report = build_domain_report(data.responses)
        payload = [item.model_dump(mode="json", by_alias=True) for item in report]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

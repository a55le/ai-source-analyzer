import json
from pathlib import Path

from ai_source_analyzer.application.dto.analysis_data import AnalysisData
from ai_source_analyzer.application.ports.reporter import ReporterPort
from ai_source_analyzer.domain.services.build_domain_report import build_domain_report
from ai_source_analyzer.infrastructure.logging import logger


class JsonReporter(ReporterPort):
    def write(self, data: AnalysisData, output_path: Path | None = None) -> None:
        if output_path is None:
            raise ValueError("Output path is required for JSON reporter")

        report = build_domain_report(data.responses)
        payload = [item.model_dump(mode="json", by_alias=True) for item in report]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        logger.info(f"Saved JSON: {output_path.name}")
import json
from pathlib import Path

from ai_source_analyzer.application.dto.analysis_data import AnalysisData
from ai_source_analyzer.application.ports.reporter import ReporterPort
from ai_source_analyzer.domain.services.build_domain_report import build_domain_report
from ai_source_analyzer.infrastructure.logging import logger


def _merge_reports_by_domain(
    existing_payload: list[dict],
    new_payload: list[dict],
) -> list[dict]:
    mentions_by_domain: dict[str, list[dict]] = {}

    for item in [*existing_payload, *new_payload]:
        if not isinstance(item, dict):
            continue

        domain = item.get("domain")
        mentions_in = item.get("mentionsIn") or []
        if not isinstance(domain, str) or not isinstance(mentions_in, list):
            continue

        mentions_by_domain.setdefault(domain, []).extend(mentions_in)

    merged = [
        {
            "domain": domain,
            "mentions": len(mentions_in),
            "mentionsIn": mentions_in,
        }
        for domain, mentions_in in mentions_by_domain.items()
    ]
    merged.sort(key=lambda item: (-item["mentions"], item["domain"]))
    return merged


class JsonReporter(ReporterPort):
    def write(
        self,
        data: AnalysisData,
        output_path: Path | None = None,
        append: bool = False,
    ) -> None:
        if output_path is None:
            raise ValueError("Output path is required for JSON reporter")

        report = build_domain_report(data.responses)
        payload = [item.model_dump(mode="json", by_alias=True) for item in report]
        merged_payload = payload

        if append and output_path.exists():
            existing_text = output_path.read_text(encoding="utf-8").strip()
            if existing_text:
                try:
                    existing_payload = json.loads(existing_text)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Cannot append: invalid JSON in {output_path}"
                    ) from error

                if not isinstance(existing_payload, list):
                    raise ValueError(
                        "Cannot append: existing report must be a JSON array"
                    )

                merged_payload = _merge_reports_by_domain(existing_payload, payload)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(merged_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        logger.info(f"Saved JSON: {output_path.name} (append={append})")

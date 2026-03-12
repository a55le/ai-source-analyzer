from dataclasses import dataclass

from ai_source_analyzer.domain.entities.llm_response import LLMResponse


@dataclass(frozen=True)
class ReportData:
    queries: list[str]
    providers: list[str]
    responses: list[LLMResponse]

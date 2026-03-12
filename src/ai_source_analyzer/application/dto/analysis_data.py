from pydantic import BaseModel

from ai_source_analyzer.domain.entities.llm_response import LLMResponse


class AnalysisData(BaseModel):
    queries: list[str]
    providers: list[str]
    responses: list[LLMResponse]

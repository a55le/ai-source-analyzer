from pydantic import BaseModel

from ai_source_analyzer.models.source import SourceItem


class LLMResponse(BaseModel):
    provider: str
    query: str
    answer_text: str
    sources: list[SourceItem]
    raw_response: dict | None = None
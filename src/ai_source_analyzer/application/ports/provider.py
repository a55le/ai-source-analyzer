from typing import Protocol

from ai_source_analyzer.domain.entities.llm_response import LLMResponse


class ProviderPort(Protocol):
    name: str
    required_env: list[str]

    def ask(self, query: str) -> LLMResponse: ...

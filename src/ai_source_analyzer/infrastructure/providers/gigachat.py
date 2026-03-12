from ai_source_analyzer.domain.entities.llm_response import LLMResponse
from ai_source_analyzer.infrastructure.providers.base import BaseProvider


class GigaChatProvider(BaseProvider):
    name = "gigachat"
    required_env = ["gigachat_api_key"]

    def ask(self, query: str) -> LLMResponse:
        raise NotImplementedError("Implement real API call here")

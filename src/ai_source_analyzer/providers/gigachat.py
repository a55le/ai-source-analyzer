from .base import BaseProvider
from ai_source_analyzer.models.response import LLMResponse


class GigaChatProvider(BaseProvider):
    name = "gigachat"
    required_env = ["s"]

    def ask(self, query: str) -> LLMResponse:
        raise NotImplementedError("Implement real API call here")
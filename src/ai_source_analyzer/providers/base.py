from abc import ABC, abstractmethod

from ai_source_analyzer.models.response import LLMResponse


class BaseProvider(ABC):
    name: str = "base"
    required_env: list[str] = []
    
    @abstractmethod
    def ask(self, query: str) -> LLMResponse:
        raise NotImplementedError
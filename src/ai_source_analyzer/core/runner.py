from ai_source_analyzer.providers.base import BaseProvider
from ai_source_analyzer.models.response import LLMResponse


class QueryRunner:
    def run_one(self, provider: BaseProvider, query: str) -> LLMResponse:
        return provider.ask(query)
    
    def run_many(
        self,
        providers: list[BaseProvider],
        queries: list[str]
    ) -> list[LLMResponse]:
        results: list[LLMResponse] = []
        
        for provider in providers:
            for query in queries:
                results.append(self.run_one(provider, query))
                
        return results
from ai_source_analyzer.application.ports.provider import ProviderPort
from ai_source_analyzer.domain.entities.llm_response import LLMResponse


class RunQueriesUseCase:
    def execute(
        self,
        providers: list[ProviderPort],
        queries: list[str],
    ) -> list[LLMResponse]:
        results: list[LLMResponse] = []

        for provider in providers:
            for query in queries:
                results.append(provider.ask(query))

        return results

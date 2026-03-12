from collections.abc import Callable

from ai_source_analyzer.application.ports.provider import ProviderPort
from ai_source_analyzer.domain.entities.llm_response import LLMResponse


class RunQueriesUseCase:
    def execute(
        self,
        providers: list[ProviderPort],
        queries: list[str],
        on_progress: Callable[[str, str, int, int], None] | None = None,
    ) -> list[LLMResponse]:
        results: list[LLMResponse] = []
        total = len(providers) * len(queries)
        completed = 0

        for provider in providers:
            for query in queries:
                results.append(provider.ask(query))
                completed += 1
                if on_progress is not None:
                    on_progress(provider.name, query, completed, total)

        return results

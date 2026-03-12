from collections import Counter

from ai_source_analyzer.models.response import LLMResponse


def get_domains_stats(responses: list[LLMResponse]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    
    for response in responses:
        for source in response.sources:
            counter[source.domain] += 1
            
    return dict(counter.most_common())
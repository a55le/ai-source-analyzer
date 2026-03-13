from collections import defaultdict
from urllib.parse import urlparse

from ai_source_analyzer.domain.entities.domain_report import (
    DomainMentionsReportItem,
    MentionLocation,
)
from ai_source_analyzer.domain.entities.llm_response import LLMResponse


def build_domain_report(
    responses: list[LLMResponse],
) -> list[DomainMentionsReportItem]:
    mentions_by_domain: dict[str, dict[tuple[str, str], MentionLocation]] = defaultdict(
        dict
    )

    for response in responses:
        for source in response.sources:
            url = str(source.url)
            domain = urlparse(url).netloc.lower()
            mentions_by_domain[domain].setdefault(
                (url, response.query),
                MentionLocation(url=url, query=response.query),
            )

    items = [
        DomainMentionsReportItem(
            domain=domain,
            mentions=len(mentions_in),
            mentions_in=list(mentions_in.values()),
        )
        for domain, mentions_in in mentions_by_domain.items()
    ]
    items.sort(key=lambda item: (-item.mentions, item.domain))
    return items


def get_domains_stats(responses: list[LLMResponse]) -> dict[str, int]:
    return {item.domain: item.mentions for item in build_domain_report(responses)}

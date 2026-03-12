from urllib.parse import urlparse

from ai_source_analyzer.providers.base import BaseProvider
from ai_source_analyzer.models.response import LLMResponse
from ai_source_analyzer.models.source import SourceItem


class MockProvider(BaseProvider):
    name = "mock"
    required_env: list[str] = []

    def ask(self, query: str) -> LLMResponse:
        raw_response = {
            "answer": f"Тестовый ответ на запрос: {query}",
            "sources": [
                {
                    "url": "https://market.yandex.ru/catalog--elektrobritvy-muzhskie/54913/list",
                    "title": "Мужские электробритвы",
                    "snippet": "Подборка и каталог товаров",
                },
                {
                    "url": "https://www.mvideo.ru/category/elektrobritvy-178",
                    "title": "Электробритвы",
                    "snippet": "Каталог электробритв",
                },
                {
                    "url": "https://journal.tinkoff.ru/list/best-shavers/",
                    "title": "Лучшие бритвы",
                    "snippet": "Подборка популярных моделей",
                },
            ],
        }

        sources: list[SourceItem] = []
        for index, item in enumerate(raw_response["sources"], start=1):
            url = item["url"]
            domain = urlparse(url).netloc.lower()

            sources.append(
                SourceItem(
                    url=url,
                    domain=domain,
                    title=item.get("title"),
                    position=index,
                )
            )

        return LLMResponse(
            provider=self.name,
            query=query,
            answer_text=raw_response["answer"],
            sources=sources,
            raw_response=raw_response,
        )
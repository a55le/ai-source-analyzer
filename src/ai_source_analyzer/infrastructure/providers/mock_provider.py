import time

from ai_source_analyzer.domain.entities.llm_response import LLMResponse
from ai_source_analyzer.domain.entities.source import SourceItem
from ai_source_analyzer.infrastructure.providers.base import BaseProvider


# class MockProvider(BaseProvider):
#     """
#     Моковый провайдер. На проде нужно будет удалить. Сделан чисто для Unit-тестирования
#     """

#     name = "mock"
#     required_env: list[str] = []

#     def ask(self, query: str) -> LLMResponse:
#         raw_response = {
#             "answer": f"Тестовый ответ на запрос: {query}",
#             "sources": [
#                 {
#                     "url": "https://market.yandex.ru/catalog--elektrobritvy-muzhskie/54913/list",
#                     "title": "Мужские электробритвы",
#                     "snippet": "Подборка и каталог товаров",
#                 },
#                 {
#                     "url": "https://www.mvideo.ru/category/elektrobritvy-178",
#                     "title": "Электробритвы",
#                     "snippet": "Каталог электробритв",
#                 },
#                 {
#                     "url": "https://journal.tinkoff.ru/list/best-shavers/",
#                     "title": "Лучшие бритвы",
#                     "snippet": "Подборка популярных моделей",
#                 },
#             ],
#         }

#         sources: list[SourceItem] = []
#         for item in raw_response["sources"]:
#             url = item["url"]

#             sources.append(
#                 SourceItem(
#                     url=url,
#                 )
#             )

#         time.sleep(5)

#         return LLMResponse(
#             provider=self.name,
#             query=query,
#             answer_text=raw_response["answer"],
#             sources=sources,
#         )

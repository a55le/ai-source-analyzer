import json
import urllib.parse
import urllib.request
import tempfile
import os

from gigachat import GigaChat, Messages, MessagesRole, Chat
from ai_source_analyzer.domain.entities.llm_response import LLMResponse
from ai_source_analyzer.domain.entities.source import SourceItem
from ai_source_analyzer.infrastructure.providers.base import BaseProvider
from ai_source_analyzer.infrastructure.config.settings import settings


CERT_URL = "https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer"


def get_cert_path() -> str:
    cert_data = urllib.request.urlopen(CERT_URL).read()

    with tempfile.NamedTemporaryFile(suffix=".cer", delete=False) as tmp:
        tmp.write(cert_data)
        tmp.flush()
        return tmp.name


class GigaChatProvider(BaseProvider):
    name = "gigachat"
    required_env = ["gigachat_api_key"]

    def ask(self, query: str) -> LLMResponse:
        ca_path = get_cert_path()

        try:
            with GigaChat(
                credentials=settings.gigachat_api_key,
                ca_bundle_file=ca_path,
            ) as giga:
                response = giga.chat(
                    Chat(
                        model="GigaChat-Max",
                        messages=[
                            Messages(
                                role=MessagesRole.SYSTEM,
                                content="""
                                    Проанализируй запрос, используя российские интернет-источники.
                                    Верни ответ строго в JSON-схеме:
                                    [
                                    {
                                        "summary": "string",
                                        "sources": [
                                        {
                                            "url": "string",
                                            "title": "string"
                                        }
                                        ]
                                    }
                                    ]
                                """.strip(),
                            ),
                            Messages(role=MessagesRole.USER, content=query),
                        ]
                    )
                )

            content = response.choices[0].message.content
            sources: list[SourceItem] = []
            answer_text = content

            try:
                data = json.loads(content)
                item = data[0] if isinstance(data, list) and data else {}
                answer_text = item.get("summary", content)

                for i, s in enumerate(item.get("sources", []), start=1):
                    url = s.get("url")
                    if not url:
                        continue

                    sources.append(
                        SourceItem(
                            url=url,
                            domain=urllib.parse.urlparse(url).netloc.lower(),
                            title=s.get("title"),
                            position=i,
                        )
                    )
            except json.JSONDecodeError:
                answer_text = content

            return LLMResponse(
                provider=self.name,
                query=query,
                answer_text=answer_text,
                sources=sources,
                raw_response={"content": content},
            )

        finally:
            if os.path.exists(ca_path):
                os.remove(ca_path)
import atexit
import json
import os
import tempfile
import urllib.parse
import urllib.request

from gigachat import Chat, GigaChat, Messages, MessagesRole

from ai_source_analyzer.domain.entities.llm_response import LLMResponse
from ai_source_analyzer.domain.entities.source import HttpUrl, SourceItem
from ai_source_analyzer.infrastructure.config.settings import settings
from ai_source_analyzer.infrastructure.providers.base import BaseProvider
from .constants import SYSTEM_PROMPT

CERT_URL = "https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer"
CERT_DOWNLOAD_TIMEOUT_SECONDS = 10
MODEL_NAME = "GigaChat-Max"

_cached_cert_path: str | None = None


def _cleanup_cached_cert() -> None:
    global _cached_cert_path
    if _cached_cert_path and os.path.exists(_cached_cert_path):
        os.remove(_cached_cert_path)
    _cached_cert_path = None


def get_cert_path() -> str:
    global _cached_cert_path

    if _cached_cert_path and os.path.exists(_cached_cert_path):
        return _cached_cert_path

    cert_data = urllib.request.urlopen(
        CERT_URL,
        timeout=CERT_DOWNLOAD_TIMEOUT_SECONDS,
    ).read()

    with tempfile.NamedTemporaryFile(suffix=".cer", delete=False) as temp_file:
        temp_file.write(cert_data)
        temp_file.flush()
        _cached_cert_path = temp_file.name

    if _cached_cert_path is None:
        raise RuntimeError("Failed to create certificate file")

    return _cached_cert_path


def _parse_content(content: str) -> tuple[str, list[SourceItem]]:
    answer_text = content
    sources: list[SourceItem] = []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return answer_text, sources

    try:
        item = data[0] if data else {}
    except Exception:
        item = data

    try:
        summary = item.get("summary")
    except Exception:
        return answer_text, sources

    if summary:
        answer_text = str(summary).strip()

    raw_sources = item.get("sources", []) or []
    for index, source in enumerate(raw_sources, start=1):
        try:
            url = str(source.get("url", ""))

            title = source.get("title")
            sources.append(
                SourceItem(
                    url=HttpUrl(url),
                    domain=urllib.parse.urlparse(url).netloc.lower(),
                    title=str(title).strip() if title else None,
                    position=index,
                )
            )
        except Exception:
            continue

    return answer_text, sources


class GigaChatProvider(BaseProvider):
    name = "gigachat"
    required_env = ["gigachat_api_key"]

    def ask(self, query: str) -> LLMResponse:
        with GigaChat(
            credentials=settings.gigachat_api_key,
            ca_bundle_file=get_cert_path(),
        ) as giga:
            response = giga.chat(
                Chat(
                    model=MODEL_NAME,
                    messages=[
                        Messages(
                            role=MessagesRole.SYSTEM,
                            content=SYSTEM_PROMPT,
                        ),
                        Messages(role=MessagesRole.USER, content=query),
                    ],
                )
            )

        content = str(response.choices[0].message.content)
        answer_text, sources = _parse_content(content)

        return LLMResponse(
            provider=self.name,
            query=query,
            answer_text=answer_text,
            sources=sources,
            raw_response={"content": content},
        )


atexit.register(_cleanup_cached_cert)
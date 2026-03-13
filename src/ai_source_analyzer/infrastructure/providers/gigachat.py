import atexit
import base64
import os
import tempfile
import urllib.request

from gigachat import Chat, GigaChat, Messages, MessagesRole
from json_repair import loads as repair_json_loads
from pydantic.networks import HttpUrl

from ai_source_analyzer.domain.entities.llm_response import LLMResponse
from ai_source_analyzer.domain.entities.source import SourceItem
from ai_source_analyzer.infrastructure.config.settings import settings
from ai_source_analyzer.infrastructure.providers.base import BaseProvider

SYSTEM_PROMPT = """
Проанализируй запрос, используя российские интернет-источники.

Верни только валидный JSON.
Не добавляй markdown, тройные кавычки, пояснения, вступительный текст, комментарии и завершающий текст.
Используй только двойные кавычки в ключах и строках.
Не используй trailing commas.

Формат ответа:
[
  {
    "summary": "string",
    "sources": [
      {
        "url": "https://example.com",
        "title": "string"
      }
    ]
  }
]
"""

CERT_URL = "https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer"
CERT_DOWNLOAD_TIMEOUT_SECONDS = 10
DEFAULT_MODEL_NAME = "GigaChat"
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

_cached_cert_path: str | None = None
_authorization_secret_hash: dict[tuple[str, str], str] = {}


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


def get_authorization_secret() -> str:
    client_id = settings.gigachat_client_id
    client_secret = settings.gigachat_client_secret

    if client_id is None or client_secret is None:
        raise ValueError("Missing gigachat_client_id or gigachat_client_secret")

    cache_key = (client_id, client_secret)
    cached = _authorization_secret_hash.get(cache_key)
    if cached is not None:
        return cached

    raw_credentials = f"{client_id}:{client_secret}"
    authorization_secret = base64.b64encode(raw_credentials.encode("utf-8")).decode(
        "utf-8"
    )
    _authorization_secret_hash[cache_key] = authorization_secret
    return authorization_secret


def _parse_content(content: str) -> tuple[str, list[SourceItem]]:
    answer_text = content
    sources: list[SourceItem] = []

    payload = _extract_json_payload(content)
    data = repair_json_loads(payload)

    item = data[0]

    summary = item.get("summary")
    answer_text = str(summary).strip()
    raw_sources = item.get("sources", [])

    for source in raw_sources:
        url = str(source.get("url", ""))

        sources.append(
            SourceItem(
                url=HttpUrl(url),
            )
        )

    return answer_text, sources


def _extract_json_payload(content: str) -> str:
    text = content.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and start < end:
        text = text[start : end + 1]

    return text


class GigaChatProvider(BaseProvider):
    name = "gigachat"
    required_env = ["gigachat_client_id", "gigachat_client_secret"]

    def ask(self, query: str) -> LLMResponse:
        with GigaChat(
            credentials=get_authorization_secret(),
            scope=GIGACHAT_SCOPE,
            ca_bundle_file=get_cert_path(),
        ) as giga:
            response = giga.chat(
                Chat(
                    model=settings.gigachat_model or DEFAULT_MODEL_NAME,
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
        )


atexit.register(_cleanup_cached_cert)

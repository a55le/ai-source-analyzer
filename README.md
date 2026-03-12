# AI Source Analyzer

CLI для запуска AI-провайдеров по списку запросов и генерации отчёта по доменам источников.

## Требования

- Python `3.13`
- Poetry

## Установка и запуск

1. Установи зависимости:

```bash
poetry install
```

2. Перед использованием войди в виртуальную оболочку Poetry:

```bash
poetry env use 3.13
eval $(poetry env activate)
```

3. Запусти программу:

```bash
ai-source-analyzer --path queries.txt
```

Сохранить JSON-отчёт:

```bash
analyze-ai-source --path queries.txt --output report.json
```

Запуск только выбранных провайдеров:

```bash
analyze-ai-source --path queries.txt --provider mock --provider gigachat
```

## CLI-параметры

- `--path`, `-p` — путь к TXT-файлу с запросами (обязательно).
- `--provider`, `-pr` — имя провайдера (можно указывать несколько раз).
- `--output`, `-o` — путь к выходному файлу отчёта.

Если `--output` не указан, используется `cli`-репортер.  
Если указан, формат определяется по расширению файла (например, `json`).

## Формат JSON-отчёта

Пример:

```json
[
  {
    "domain": "market.yandex.ru",
    "mentions": 6,
    "mentionsIn": [
      {
        "url": "https://market.yandex.ru/catalog--elektrobritvy-muzhskie/54913/list",
        "query": "топ мужских бритв"
      }
    ]
  }
]
```

`mentions` всегда равно количеству элементов в `mentionsIn`.

## Как добавить свой провайдер

1. Создай файл в `src/ai_source_analyzer/infrastructure/providers/`, например `my_provider.py`.
2. Наследуйся от `BaseProvider` из `infrastructure/providers/base.py`.
3. Реализуй `ask(query) -> LLMResponse`.
4. Укажи `name` и `required_env`.
5. Добавь нужные поля в `infrastructure/config/settings.py` и ключи в `.env`.

Минимальный шаблон:

```python
from ai_source_analyzer.infrastructure.providers.base import BaseProvider
from ai_source_analyzer.domain.entities.llm_response import LLMResponse


class MyProvider(BaseProvider):
    name = "my_provider"
    required_env = ["my_provider_api_key"]  # имя поля в Settings

    def ask(self, query: str) -> LLMResponse:
        # Тут делай реальный запрос к API нейросети и выдача LLMResponse класса
        raise NotImplementedError
```

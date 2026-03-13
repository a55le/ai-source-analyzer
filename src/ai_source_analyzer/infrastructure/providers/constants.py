SYSTEM_PROMPT = """
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
"""
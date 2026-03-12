from pathlib import Path

from ai_source_analyzer.application.ports.query_reader import QueryReaderPort


class QueryFileReader(QueryReaderPort):
    def read(self, path: Path) -> list[str]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_text(encoding="utf-8")
        queries = [line.strip() for line in content.splitlines() if line.strip()]

        if not queries:
            raise ValueError("No queries found in file")

        return queries
from pathlib import Path
from typing import Protocol


class QueryReaderPort(Protocol):
    def read(self, path: Path) -> list[str]: ...

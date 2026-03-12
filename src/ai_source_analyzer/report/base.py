from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ai_source_analyzer.models.response import LLMResponse


@dataclass(frozen=True)
class ReportData:
    queries: list[str]
    providers: list[str]
    responses: list[LLMResponse]


class BaseReporter(ABC):
    @abstractmethod
    def write(self, data: ReportData, output_path: Path | None = None) -> None:
        raise NotImplementedError

from abc import ABC, abstractmethod
from pathlib import Path

from ai_source_analyzer.application.dto.analysis_data import AnalysisData


class ReporterPort(ABC):
    @abstractmethod
    def write(
        self,
        data: AnalysisData,
        output_path: Path | None = None,
        append: bool = False,
    ) -> None:
        raise NotImplementedError

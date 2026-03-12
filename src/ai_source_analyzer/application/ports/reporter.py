from abc import ABC, abstractmethod
from pathlib import Path

from ai_source_analyzer.application.dto.report_data import ReportData


class ReporterPort(ABC):
    @abstractmethod
    def write(self, data: ReportData, output_path: Path | None = None) -> None:
        raise NotImplementedError

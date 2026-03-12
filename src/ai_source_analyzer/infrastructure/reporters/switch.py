from .cli_reporter import CliReporter
from .json_reporter import JsonReporter
from ai_source_analyzer.application.ports.reporter import ReporterPort

def getReporter(ext: str) -> ReporterPort:
    match ext:
        case "json":
            return JsonReporter()
        case "cli":
            return CliReporter()
        case _:
            raise ValueError(f"Unsupported output file extension: {ext}")
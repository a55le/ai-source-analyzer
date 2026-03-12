from rich.console import Console

from ai_source_analyzer.application.ports.logger import LoggerPort


class Logger(LoggerPort):
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def warn(self, message: str) -> None:
        self._console.print(f"[bold yellow][WARN][/bold yellow] {message}")

    def info(self, message: str) -> None:
        self._console.print(f"[bold blue][INFO][/bold blue] {message}")

    def error(self, message: str) -> None:
        self._console.print(f"[bold red][ERROR][/bold red] {message}")


logger = Logger()

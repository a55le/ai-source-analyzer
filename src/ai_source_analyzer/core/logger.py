from rich.console import Console

class Logger():
    def __init__(self):
        self._console = Console()
        
    def warn(self, s: str) -> None:
        self._console.print(f"[bold yellow][WARN][/bold yellow] {s}")
        
    def log(self, s: str) -> None:
        self._console.print(f"[bold blue][INFO][/bold blue] {s}")
        
    def error(self, s: str) -> None:
        self._console.print(f"[bold red][ERROR][/bold red] {s}")
        
logger = Logger()
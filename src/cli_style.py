import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

console = Console()

def show_header(title: str) -> None:
    header_text = Text.assemble(
        ("─" * 4 + " ", "cyan"),
        (title.upper(), "bold magenta"),
        (" " + "─" * 4, "cyan")
    )
    console.print(header_text, justify="center")

def pretty_log(*args: str) -> None:
    """
    Print logs in a Rich panel. If the text is valid JSON, pretty-print it.
    """
    combined = " ".join(str(arg) for arg in args).strip()
    if combined.startswith("{") or combined.startswith("["):
        try:
            parsed = json.loads(combined)
            combined = json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
    panel = Panel.fit(combined, style="bold white on black")
    console.print(panel)

def ask_user(prompt_text: str) -> str:
    """
    Ask a user for input using a Rich prompt.
    """
    return Prompt.ask(Text(prompt_text, style="bold yellow"))

class ResearchProgressDisplay:
    """
    Helper to show a Rich-based progress bar across Depth, Breadth, and Queries.
    Keeps the bar at the bottom, updated in place.
    """
    def __init__(self):
        self.progress = Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=20),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            transient=False  # keep the progress bars pinned at the bottom
        )
        self.depth_task = None
        self.breadth_task = None
        self.queries_task = None

    def start(self, total_depth: int, total_breadth: int, total_queries: int) -> None:
        self.progress.start()
        self.depth_task = self.progress.add_task("Depth", total=total_depth)
        self.breadth_task = self.progress.add_task("Breadth", total=total_breadth)
        self.queries_task = self.progress.add_task("Queries", total=total_queries)

    def update(self, current_depth: int, total_depth: int,
               current_breadth: int, total_breadth: int,
               completed_queries: int, total_queries: int,
               current_query: str = None) -> None:
        depth_done = total_depth - current_depth
        breadth_done = total_breadth - current_breadth

        self.progress.update(self.depth_task, completed=depth_done)
        self.progress.update(self.breadth_task, completed=breadth_done)
        self.progress.update(self.queries_task, completed=completed_queries)

        if current_query:
            console.print(f"[green]Current[/green]: [italic]{current_query}[/italic]", highlight=False)

    def stop(self) -> None:
        self.progress.stop()

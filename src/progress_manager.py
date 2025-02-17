import os
import sys

class ProgressManager:
    def __init__(self):
        self.last_progress = None
        self.progress_lines = 4  # Fixed number of lines for progress display
        sys.stdout.write('\n' * self.progress_lines)
        sys.stdout.flush()

    def get_terminal_size(self):
        try:
            return os.get_terminal_size()
        except OSError:
            return os.terminal_size((80, 24))

    def draw_progress_bar(self, label: str, value: int, total: int, char: str = '=') -> str:
        term = self.get_terminal_size()
        width = min(30, term.columns - 20) if term.columns else 30
        percent = (value / total) * 100 if total else 0
        filled = round((width * percent) / 100)
        empty = width - filled
        return f"{label} [{char * filled}{' ' * empty}] {round(percent)}%"

    def update_progress(self, progress):
        self.last_progress = progress
        term = self.get_terminal_size()
        terminal_height = term.lines if term.lines else 24
        progress_start = terminal_height - self.progress_lines

        sys.stdout.write(f"\x1B[{progress_start};1H\x1B[0J")

        lines = [
            self.draw_progress_bar("Depth:   ", progress.total_depth - progress.current_depth, progress.total_depth, '█'),
            self.draw_progress_bar("Breadth: ", progress.total_breadth - progress.current_breadth, progress.total_breadth, '█'),
            self.draw_progress_bar("Queries: ", progress.completed_queries, progress.total_queries, '█'),
        ]

        if getattr(progress, 'current_query', None):
            lines.append(f"Current:  {progress.current_query}")

        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.write(f"\x1B[{self.progress_lines}A")
        sys.stdout.flush()

    def stop(self):
        sys.stdout.write(f"\x1B[{self.progress_lines}B\n")
        sys.stdout.flush()

import os
import sys

class OutputManager:
    def __init__(self):
        self.progress_lines = 4
        self.progress_area = []
        self.initialized = False
        sys.stdout.write('\n' * self.progress_lines)
        sys.stdout.flush()
        self.initialized = True

    def log(self, *args):
        if self.initialized:
            sys.stdout.write(f"\x1B[{self.progress_lines}A")
            sys.stdout.write("\x1B[0J")
        print(*args)
        if self.initialized:
            self.draw_progress()

    def update_progress(self, progress):
        self.progress_area = [
            f"Depth:    [{self.get_progress_bar(progress.total_depth - progress.current_depth, progress.total_depth)}] "
            f"{round((progress.total_depth - progress.current_depth) / progress.total_depth * 100)}%",
            f"Breadth:  [{self.get_progress_bar(progress.total_breadth - progress.current_breadth, progress.total_breadth)}] "
            f"{round((progress.total_breadth - progress.current_breadth) / progress.total_breadth * 100)}%",
            f"Queries:  [{self.get_progress_bar(progress.completed_queries, progress.total_queries)}] "
            f"{round(progress.completed_queries / progress.total_queries * 100)}%",
            f"Current:  {progress.current_query}" if getattr(progress, 'current_query', None) else ''
        ]
        self.draw_progress()

    def get_progress_bar(self, value, total):
        try:
            cols = os.get_terminal_size().columns
            width = min(30, cols - 20)
        except OSError:
            width = 30
        filled = round((width * value) / total)
        return '█' * filled + ' ' * (width - filled)

    def draw_progress(self):
        if not self.initialized or not self.progress_area:
            return
        try:
            terminal_height = os.get_terminal_size().lines
        except OSError:
            terminal_height = 24
        sys.stdout.write(f"\x1B[{terminal_height - self.progress_lines};1H")
        sys.stdout.write("\n".join(self.progress_area))
        sys.stdout.write(f"\x1B[{terminal_height - self.progress_lines - 1};1H")
        sys.stdout.flush()

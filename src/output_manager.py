import sys
import os

class OutputManager:
    def __init__(self):
        self.progress_lines = 4
        self.progress_area = []
        self.initialized = False
        sys.stdout.write('\n' * self.progress_lines)
        sys.stdout.flush()
        self.initialized = True

    def log(self, *args):
        if os.getenv("DEBUG_LOGS"):
            print(*args)
            return

        if self.initialized:
            sys.stdout.write(f"\x1B[{self.progress_lines}A")
            sys.stdout.write("\x1B[0J")
        print(*args)
        if self.initialized:
            self.draw_progress()

    def update_progress(self, progress):
        depth_done = progress.total_depth - progress.current_depth
        breadth_done = progress.total_breadth - progress.current_breadth
        if progress.total_depth:
            depth_pct = round(depth_done / progress.total_depth * 100)
        else:
            depth_pct = 0
        if progress.total_breadth:
            breadth_pct = round(breadth_done / progress.total_breadth * 100)
        else:
            breadth_pct = 0
        if progress.total_queries:
            queries_pct = round(progress.completed_queries / progress.total_queries * 100)
        else:
            queries_pct = 0

        self.progress_area = [
            f"Depth:    [{self.get_progress_bar(depth_done, progress.total_depth)}] {depth_pct}%",
            f"Breadth:  [{self.get_progress_bar(breadth_done, progress.total_breadth)}] {breadth_pct}%",
            f"Queries:  [{self.get_progress_bar(progress.completed_queries, progress.total_queries)}] {queries_pct}%",
            f"Current:  {progress.current_query}" if getattr(progress, 'current_query', None) else ''
        ]
        self.draw_progress()

    def get_progress_bar(self, value, total):
        width = 30
        if total == 0:
            filled = 0
        else:
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

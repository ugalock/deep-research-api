from cli_style import pretty_log, ResearchProgressDisplay

class OutputManager:
    """
    Manages console output and progress display via Rich-based styling.
    """

    def __init__(self, verbose: bool = False):
        self.progress_display = ResearchProgressDisplay()
        self.initialized = False
        self.verbose = verbose

    def debug(self, *args):
        """
        Prints logs only if verbose mode is enabled.
        """
        if self.verbose:
            pretty_log(*args)

    def info(self, *args):
        """
        Always prints logs (for user interactions or final important messages).
        """
        pretty_log(*args)

    def update_progress(self, progress):
        """
        If not initialized, start the progress bars. Then update them.
        """
        if not self.initialized:
            self.progress_display.start(
                total_depth=progress.total_depth,
                total_breadth=progress.total_breadth,
                total_queries=progress.total_queries
            )
            self.initialized = True

        self.progress_display.update(
            current_depth=progress.current_depth,
            total_depth=progress.total_depth,
            current_breadth=progress.current_breadth,
            total_breadth=progress.total_breadth,
            completed_queries=progress.completed_queries,
            total_queries=progress.total_queries,
            current_query=getattr(progress, 'current_query', None)
        )

    def stop_progress(self):
        self.progress_display.stop()

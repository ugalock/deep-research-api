from cli_style import ResearchProgressDisplay

class ProgressManager:
    """
    Legacy manager replaced by the Rich-based progress in OutputManager.
    We keep this for compatibility, but direct all calls to the new display.
    """
    def __init__(self):
        self.research_progress_display = ResearchProgressDisplay()
        self.last_progress = None
        self.initialized = False

    def update_progress(self, progress):
        if not self.initialized:
            self.research_progress_display.start(
                total_depth=progress.total_depth,
                total_breadth=progress.total_breadth,
                total_queries=progress.total_queries
            )
            self.initialized = True

        self.research_progress_display.update(
            current_depth=progress.current_depth,
            total_depth=progress.total_depth,
            current_breadth=progress.current_breadth,
            total_breadth=progress.total_breadth,
            completed_queries=progress.completed_queries,
            total_queries=progress.total_queries,
            current_query=getattr(progress, 'current_query', None)
        )
        self.last_progress = progress

    def stop(self):
        self.research_progress_display.stop()

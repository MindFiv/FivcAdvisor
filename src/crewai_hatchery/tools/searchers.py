from crewai_tools import (
    SerperDevTool,
    # SerplyWebSearchTool,
)

web_searcher = SerperDevTool()

__all__ = ["web_searcher"]

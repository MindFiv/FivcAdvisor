from crewai_tools import (
    SerperDevTool,
    # SerplyWebSearchTool,
    ScrapeWebsiteTool,
)

web_searcher = SerperDevTool()
web_scraper = ScrapeWebsiteTool()

__all__ = ["web_searcher", "web_scraper"]

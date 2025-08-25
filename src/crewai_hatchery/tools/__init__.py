def create_tools_retriever(*args, **kwargs):
    """Create a tools retriever tool."""
    from .patches import create_tools_patch

    create_tools_patch()  # apply patches

    from .retrievers import ToolsRetriever

    retriever = ToolsRetriever(*args, **kwargs)

    from crewai_tools import (
        ScrapeWebsiteTool,
        # WebsiteSearchTool,
        # YoutubeChannelSearchTool,
        # YoutubeVideoSearchTool,
        # ZapierActionTools,
    )

    # add a fow default tools
    # retriever.add(retriever.to_tool())
    # retriever.add(SeleniumScrapingTool)
    retriever.add(ScrapeWebsiteTool())

    # custom tools
    from .calculators import basic_calculator

    retriever.add(basic_calculator)

    from .clocks import local_clock

    retriever.add(local_clock)
    # retriever.add(online_clock)

    from .searchers import web_searcher

    retriever.add(web_searcher)

    return retriever

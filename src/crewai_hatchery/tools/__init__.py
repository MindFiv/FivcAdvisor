def create_tools_retriever(*args, **kwargs):
    """Create a tools retriever tool."""
    from .patches import create_tools_patch

    create_tools_patch()  # apply patches

    from .retrievers import ToolsRetriever

    retriever = ToolsRetriever(*args, **kwargs)

    from crewai_tools import (
        DirectoryReadTool,
        DirectorySearchTool,
        FileReadTool,
        FileWriterTool,
        ScrapeWebsiteTool,
        WebsiteSearchTool,
        # YoutubeChannelSearchTool,
        # YoutubeVideoSearchTool,
        # ZapierActionTools,
    )
    from .calculators import basic_calculator
    from .clocks import local_clock, online_clock

    # add a fow default tools
    # retriever.add(retriever.to_tool())
    retriever.add(DirectoryReadTool())
    retriever.add(DirectorySearchTool())
    retriever.add(FileReadTool())
    retriever.add(FileWriterTool())
    # retriever.add(RagTool())
    # retriever.add(SeleniumScrapingTool)
    retriever.add(ScrapeWebsiteTool())
    retriever.add(WebsiteSearchTool())

    # custom tools
    retriever.add(basic_calculator)
    retriever.add(local_clock)
    retriever.add(online_clock)

    return retriever

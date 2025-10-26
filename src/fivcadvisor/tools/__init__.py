__all__ = [
    "register_default_tools",
    "default_retriever",
    "ToolsConfig",
    "ToolsRetriever",
    "ToolsBundle",
    "ToolsBundleManager",
    "ToolsLoader",
]

from typing import Optional

from fivcadvisor.utils import create_lazy_value
from fivcadvisor.tools.types import (
    ToolsRetriever,
    ToolsConfig,
    ToolsBundle,
    ToolsBundleManager,
    ToolsLoader,
)


def register_default_tools(tools_retriever: Optional[ToolsRetriever] = None, **kwargs):
    """
    Register default tools with the tools retriever.

    Note: Default tools from strands_tools have been removed.
    Tools are now loaded from MCP servers using ToolsLoader.

    Args:
        tools_retriever: The ToolsRetriever instance to register tools with
        **kwargs: Additional arguments (ignored)

    Returns:
        Empty list (no default tools registered)
    """
    assert tools_retriever is not None

    # Default tools from strands_tools are no longer available
    # Tools should be loaded from MCP servers using ToolsLoader instead
    # Example:
    #   loader = ToolsLoader(retriever=tools_retriever)
    #   loader.load()

    return []


def _load_retriever() -> ToolsRetriever:
    """Load and initialize the default tools retriever.

    This creates a ToolsRetriever and loads MCP tools from configured servers.
    """
    retriever = ToolsRetriever()
    register_default_tools(tools_retriever=retriever)

    # Load MCP tools using ToolsLoader
    loader = ToolsLoader(retriever=retriever)
    loader.load()

    print(f"Registered Tools: {[t.name for t in retriever.get_all()]}")
    return retriever


default_retriever = create_lazy_value(_load_retriever)

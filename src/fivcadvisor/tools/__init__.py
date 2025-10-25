__all__ = [
    "register_default_tools",
    "register_mcp_tools",
    "default_retriever",
    "ToolsConfig",
    "ToolsRetriever",
    "ToolsBundle",
    "ToolsBundleManager",
]

# import atexit
import os
from typing import Optional

from fivcadvisor.tools.compat import MCPClientInitializationError

from fivcadvisor.utils import create_lazy_value
from fivcadvisor.tools.types import (
    ToolsRetriever,
    ToolsConfig,
    ToolsBundle,
    ToolsBundleManager,
)


def register_default_tools(tools_retriever: Optional[ToolsRetriever] = None, **kwargs):
    """
    Register default tools with the tools retriever.

    Note: Default tools from strands_tools have been removed.
    Tools are now primarily loaded from MCP servers via register_mcp_tools().

    Args:
        tools_retriever: The ToolsRetriever instance to register tools with
        **kwargs: Additional arguments (ignored)

    Returns:
        Empty list (no default tools registered)
    """
    assert tools_retriever is not None

    # Default tools from strands_tools are no longer available
    # Tools should be loaded from MCP servers instead
    # See register_mcp_tools() for MCP tool loading

    return []


def register_mcp_tools(
    tools_retriever: Optional[ToolsRetriever] = None,
    **kwargs,
):
    """Create tools for MCP server with bundle support."""
    assert tools_retriever is not None

    config_file = os.environ.get("MCP_FILE", "mcp.yaml")
    config_file = os.path.abspath(config_file)

    config = ToolsConfig(config_file=config_file)
    for client_name, client_config in config._configs.items():
        try:
            client = client_config.get_client()
            tools = client.start().list_tools_sync()
            # atexit.register(lambda: c.stop(None, None, None))
            # tools.pagination_token

            # Get bundle name from config or use client name as default
            bundle_name = client_config.get("bundle", client_name)

            # Add tools with bundle information
            tools_retriever.add_batch(tools, tool_bundle=bundle_name)

        except MCPClientInitializationError as e:
            # c.stop(None, None, None)  # fixme
            print(f"Error loading tools from {client_name}: {e}")
            continue

    return config


def _load_retriever() -> ToolsRetriever:
    retriever = ToolsRetriever()
    register_default_tools(tools_retriever=retriever)
    # register_mcp_tools(tools_retriever=retriever)
    print(f"Registered Tools: {[t.tool_name for t in retriever.get_all()]}")
    return retriever


default_retriever = create_lazy_value(_load_retriever)

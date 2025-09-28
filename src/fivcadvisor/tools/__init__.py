__all__ = [
    "register_default_tools",
    "register_mcp_tools",
    "default_retriever",
    "ToolsRetriever",
]

from typing import Optional

from fivcadvisor.utils import create_lazy_value
from fivcadvisor.tools.types import ToolsRetriever, ToolsConfig


def register_default_tools(tools_retriever: Optional[ToolsRetriever] = None, **kwargs):
    assert tools_retriever is not None

    from strands.tools.registry import ToolRegistry
    from strands_tools import (
        calculator,
        current_time,
        # think,
        python_repl,
        # retrieve,
        # browser,
    )

    r = ToolRegistry()
    tool_names = r.process_tools(
        [
            calculator,
            current_time,
            # think,
            python_repl,
            # retrieve,
            # browser,
        ]
    )
    tools = [r.registry.get(name) for name in tool_names]
    tools_retriever.add_batch(tools)

    return tools


def register_mcp_tools(
    tools_retriever: Optional[ToolsRetriever] = None,
    config_file: str = "mcp.json",
    **kwargs,
):
    """Create tools for MCP server."""
    assert tools_retriever is not None

    config = ToolsConfig(config_file=config_file)
    for c in config.get_clients():
        tools = c.list_tools_sync()
        tools_retriever.add_batch(tools)
        # tools.pagination_token

    return config


def _load_retriever() -> ToolsRetriever:
    retriever = ToolsRetriever()
    register_default_tools(tools_retriever=retriever)
    register_mcp_tools(tools_retriever=retriever)
    return retriever


default_retriever = create_lazy_value(_load_retriever)

__all__ = [
    "register_default_tools",
    "register_mcp_tools",
    "default_retriever",
    "ToolsRetriever",
]

import atexit
import os
from typing import Optional

from strands.types.exceptions import MCPClientInitializationError

from fivcadvisor.utils import create_lazy_value
from fivcadvisor.tools.types import ToolsRetriever, ToolsConfig


def register_default_tools(tools_retriever: Optional[ToolsRetriever] = None, **kwargs):
    assert tools_retriever is not None

    from strands.tools.registry import ToolRegistry
    from strands_tools import (
        calculator,
        current_time,
        python_repl,
        # swarm,
        # workflow,
        # retrieve,
        # browser,
    )

    r = ToolRegistry()
    tool_names = r.process_tools(
        [
            calculator,
            current_time,
            python_repl,
            # swarm,
            # workflow,
            # retrieve,
            # browser,
        ]
    )
    tools = [r.registry.get(name) for name in tool_names]
    tools_retriever.add_batch(tools)

    return tools


def register_mcp_tools(
    tools_retriever: Optional[ToolsRetriever] = None,
    **kwargs,
):
    """Create tools for MCP server."""
    assert tools_retriever is not None

    config_file = os.environ.get("MCP_FILE", "mcp.yaml")
    config_file = os.path.abspath(config_file)

    config = ToolsConfig(config_file=config_file)
    for c in config.get_clients():
        try:
            tools = c.start().list_tools_sync()
            atexit.register(lambda: c.stop(None, None, None))
            # tools.pagination_token
        except MCPClientInitializationError as e:
            c.stop(None, None, None)  # fixme
            print(f"Error loading tools from {c}: {e}")
            continue

        tools_retriever.add_batch(tools)

    return config


def _load_retriever() -> ToolsRetriever:
    retriever = ToolsRetriever()
    register_default_tools(tools_retriever=retriever)
    register_mcp_tools(tools_retriever=retriever)
    print(f"Registered Tools: {[t.tool_name for t in retriever.get_all()]}")
    return retriever


default_retriever = create_lazy_value(_load_retriever)

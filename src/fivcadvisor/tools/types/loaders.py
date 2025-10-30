import asyncio
import os
from typing import Optional

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from fivcadvisor.tools.types.configs import ToolsConfig
from fivcadvisor.tools.types.retrievers import ToolsRetriever


class ToolsLoader(object):
    """Loader for MCP tools using langchain-mcp-adapters.

    This class manages loading tools from MCP servers configured in ToolsConfig
    and registering them with a ToolsRetriever.
    """

    def __init__(
        self,
        tools_retriever: Optional[ToolsRetriever] = None,
        config_file: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the tools loader.

        Args:
            tools_retriever: The ToolsRetriever instance to register tools with
            config_file: Path to MCP configuration file (defaults to mcp.yaml)
            **kwargs: Additional arguments (ignored)
        """
        assert tools_retriever is not None
        # Use provided config_file or get from environment
        if config_file is None:
            config_file = os.environ.get("MCP_FILE", "mcp.yaml")
        config_file = os.path.abspath(config_file)

        self.config = ToolsConfig(config_file=config_file)
        self.tools_retriever = tools_retriever

    def load(self):
        """Load tools synchronously.

        This is a convenience method that handles event loop management
        for synchronous contexts.
        """
        asyncio.run(self.load_async())

    async def load_async(self):
        """Load tools from configured MCP servers and register them.

        Uses langchain-mcp-adapters to connect to MCP servers and load their tools,
        organizing them by bundle and registering with the retriever.
        """
        client = MultiServerMCPClient({
            server_name: self.config.get(server_name).connection for
            server_name in self.config.list()
        })

        for bundle_name in client.connections:
            print(f"Connected to {bundle_name}")
            try:
                async with client.session(bundle_name) as session:
                    tools = await load_mcp_tools(session)
                    if tools:
                        self.tools_retriever.add_batch(
                            tools, tool_bundle=bundle_name)
            except Exception as e:
                print(f"Error loading tools from {bundle_name}: {e}")
                continue

    def cleanup(self):
        """Clean up resources."""
        # MultiServerMCPClient handles cleanup automatically
        self.tools_retriever.cleanup()

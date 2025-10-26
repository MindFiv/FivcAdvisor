import asyncio
import os
from typing import Optional

from fivcadvisor.tools.types.configs import ToolsConfig
from fivcadvisor.tools.types.retrievers import ToolsRetriever


class ToolsLoader(object):
    """Loader for MCP tools using langchain-mcp-adapters.

    This class manages loading tools from MCP servers configured in ToolsConfig
    and registering them with a ToolsRetriever.
    """

    def __init__(
        self,
        retriever: Optional[ToolsRetriever] = None,
        config_file: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the tools loader.

        Args:
            retriever: The ToolsRetriever instance to register tools with
            config_file: Path to MCP configuration file (defaults to mcp.yaml)
            **kwargs: Additional arguments (ignored)
        """
        assert retriever is not None
        self.retriever = retriever

        # Use provided config_file or get from environment
        if config_file is None:
            config_file = os.environ.get("MCP_FILE", "mcp.yaml")
        config_file = os.path.abspath(config_file)

        self.config = ToolsConfig(config_file=config_file)
        self.mcp_client = None

    def load(self):
        """Load tools synchronously.

        This is a convenience method that handles event loop management
        for synchronous contexts.
        """
        try:
            asyncio.run(self.load_async())
        except RuntimeError:
            # If event loop is already running, use get_event_loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule as a task instead
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.submit(asyncio.run, self.load_async())
            else:
                loop.run_until_complete(self.load_async())

    async def load_async(self):
        """Load tools from configured MCP servers and register them.

        Uses langchain-mcp-adapters to connect to MCP servers and load their tools,
        organizing them by bundle and registering with the retriever.
        """
        self.mcp_client = self.config.get_mcp_client()
        if self.mcp_client is None:
            print("No valid MCP configurations found")
            return

        # Load tools from all configured MCP servers
        tools_by_bundle = {}

        # Get tools from each configured server
        for server_name, server_config in self.config._configs.items():
            if not isinstance(server_config, dict):
                continue

            try:
                # Get bundle name from config or use server name as default
                bundle_name = server_config.get("bundle", server_name)

                # Get tools for this server
                async with self.mcp_client.session(server_name) as session:
                    from langchain_mcp_adapters.tools import load_mcp_tools

                    tools = await load_mcp_tools(session)
                    if tools:
                        if bundle_name not in tools_by_bundle:
                            tools_by_bundle[bundle_name] = []
                        tools_by_bundle[bundle_name].extend(tools)

            except Exception as e:
                print(f"Error loading tools from {server_name}: {e}")
                continue

        # Register all tools with their bundles
        for bundle_name, tools in tools_by_bundle.items():
            self.retriever.add_batch(tools, tool_bundle=bundle_name)

    def cleanup(self):
        """Clean up resources."""
        # MultiServerMCPClient handles cleanup automatically
        self.mcp_client = None

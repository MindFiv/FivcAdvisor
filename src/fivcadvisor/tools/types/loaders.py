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
    and registering them with a ToolsRetriever. It supports incremental updates,
    automatically adding new bundles and removing tools from bundles that are
    no longer configured.

    Attributes:
        config: ToolsConfig instance for loading MCP server configurations
        tools_retriever: ToolsRetriever instance to register tools with
        tools_bundles: Dictionary mapping bundle names to sets of tool names
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
            config_file: Path to MCP configuration file (defaults to mcp.yaml).
                        If not provided, uses MCP_FILE environment variable or "mcp.yaml"
            **kwargs: Additional arguments (ignored)

        Raises:
            AssertionError: If tools_retriever is None
        """
        assert tools_retriever is not None
        # Use provided config_file or get from environment
        if config_file is None:
            config_file = os.environ.get("MCP_FILE", "mcp.yaml")
        config_file = os.path.abspath(config_file)

        # Initialize config with load=False to defer loading until load_async() is called
        self.config = ToolsConfig(config_file=config_file, load=False)
        self.tools_retriever = tools_retriever
        # Track tools by bundle for incremental updates
        self.tools_bundles: dict[str, set[str]] = {}

    def load(self):
        """Load tools synchronously.

        This is a convenience method that handles event loop management
        for synchronous contexts.
        """
        asyncio.run(self.load_async())

    async def load_async(self):
        """Load tools from configured MCP servers and register them.

        Performs incremental updates:
        - Loads config from file
        - Connects to MCP servers and loads their tools
        - Adds new bundles and their tools to the retriever
        - Removes tools from bundles that are no longer configured
        - Organizes tools by bundle and registers with the retriever

        The method handles errors gracefully, continuing to load other bundles
        if one fails.
        """
        self.config.load()
        errors = self.config.get_errors()
        if errors:
            print(f"Errors loading config: {errors}")
            return

        client = MultiServerMCPClient(
            {
                server_name: self.config.get(server_name).connection
                for server_name in self.config.list()
            }
        )
        bundle_names_target = set(client.connections.keys())
        bundle_names_now = set(self.tools_bundles.keys())

        bundle_names_to_remove = bundle_names_now - bundle_names_target
        bundle_names_to_add = bundle_names_target - bundle_names_now

        for bundle_name in bundle_names_to_add:
            try:
                async with client.session(bundle_name) as session:
                    tools = await load_mcp_tools(session)
                    if tools:
                        self.tools_retriever.add_batch(tools, tool_bundle=bundle_name)
                        self.tools_bundles.setdefault(bundle_name, {t.name for t in tools})

            except Exception as e:
                print(f"Error loading tools from {bundle_name}: {e}")
                continue

        for bundle_name in bundle_names_to_remove:
            for tool_name in self.tools_bundles.pop(
                    bundle_name, set()
            ):
                self.tools_retriever.remove(tool_name)

    # def get_tools_bundles(self) -> dict[str, set[str]]:
    #     return self.tools_bundles.copy()

    def cleanup(self):
        """Clean up resources and remove all loaded tools.

        Removes all tools that were loaded from MCP servers from the retriever
        and clears the tools_bundles tracking dictionary.

        This should be called when the loader is no longer needed to ensure
        proper cleanup of resources.
        """
        # Remove all tracked tools from the retriever
        for tool_bundle in self.tools_bundles.values():
            for tool_name in tool_bundle:
                self.tools_retriever.remove(tool_name)

        # Clear the bundle tracking
        self.tools_bundles.clear()

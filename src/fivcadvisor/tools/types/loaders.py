import asyncio
import os
from typing import Optional

from langchain_mcp_adapters.client import MultiServerMCPClient

from fivcadvisor.tools.types.configs import ToolsConfig
from fivcadvisor.tools.types.retrievers import ToolsRetriever


class ToolsLoader(object):
    """Loader for MCP tools using langchain-mcp-adapters.

    This class manages loading tools from MCP servers configured in ToolsConfig
    and registering them with a ToolsRetriever. It supports incremental updates,
    automatically adding new bundles and removing tools from bundles that are
    no longer configured.

    Sessions are created within async with blocks for proper lifecycle management,
    ensuring clean resource handling and avoiding async generator cleanup issues.

    Attributes:
        config: ToolsConfig instance for loading MCP server configurations
        tools_retriever: ToolsRetriever instance to register tools with
        tools_bundles: Dictionary mapping bundle names to sets of tool names
        client: Persistent MultiServerMCPClient instance
        sessions: Dictionary for session tracking (kept for compatibility)
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
        # Persistent MCP client and sessions
        self.client: Optional[MultiServerMCPClient] = None

    async def load_async(self):
        """Load tools from configured MCP servers and register them.

        Performs incremental updates:
        - Loads config from file
        - Creates persistent MCP client
        - Connects to MCP servers and loads their tools
        - Adds new bundles and their tools to the retriever
        - Removes tools from bundles that are no longer configured

        The method handles errors gracefully, continuing to load other bundles
        if one fails. Sessions are created within async with blocks for proper
        lifecycle management.
        """
        self.config.load()
        errors = self.config.get_errors()
        if errors:
            print(f"Errors loading config: {errors}")
            return

        # Create persistent client (kept alive during app runtime)
        self.client = MultiServerMCPClient(
            {
                server_name: self.config.get(server_name).connection
                for server_name in self.config.list()
            }
        )
        bundle_names_target = set(self.client.connections.keys())
        bundle_names_now = set(self.tools_bundles.keys())

        bundle_names_to_remove = bundle_names_now - bundle_names_target
        bundle_names_to_add = bundle_names_target - bundle_names_now

        # Remove tools from bundles that are no longer configured
        for bundle_name in bundle_names_to_remove:
            for tool_name in self.tools_bundles.pop(bundle_name, set()):
                self.tools_retriever.remove(tool_name)

        # Load tools for new bundles using proper async context management

        for bundle_name in bundle_names_to_add:
            try:
                # Use async with for proper session lifecycle management
                tools = await self.client.get_tools(server_name=bundle_name)
                if tools:
                    self.tools_retriever.add_batch(tools)
                    self.tools_bundles.setdefault(bundle_name, {t.name for t in tools})

            except Exception as e:
                print(f"Error loading tools from {bundle_name}: {e}")
                continue

    def load(self):
        """Load tools synchronously.

        This is a convenience method that handles event loop management
        for synchronous contexts.
        """
        asyncio.run(self.load_async())

    async def cleanup_async(self):
        """Asynchronously clean up MCP resources.

        Removes all loaded tools from the retriever and clears the client reference.
        This should be called when the application is shutting down.
        """
        # Remove all tracked tools from the retriever
        for tool_bundle in self.tools_bundles.values():
            for tool_name in tool_bundle:
                self.tools_retriever.remove(tool_name)

        # Clear the bundle tracking and client reference
        self.tools_bundles.clear()
        self.client = None

    def cleanup(self):
        """Synchronous cleanup wrapper for cleanup_async.

        This is a convenience method for synchronous contexts.
        """
        asyncio.run(self.cleanup_async())

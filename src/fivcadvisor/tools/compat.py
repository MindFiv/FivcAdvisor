"""
Tool compatibility layer for Strands → LangChain migration.

This module provides tool definitions that maintain compatibility with the
Strands API while using LangChain 1.0 tools under the hood.

Key Types:
    - AgentTool: LangChain Tool for tool compatibility
    - MCPClient: Wrapper for MCP client connections
    - MCPClientInitializationError: Exception for MCP client errors

Strategy:
    We use LangChain's Tool class directly, which is more mature and provides
    better integration with the LangChain ecosystem. This replaces Strands'
    AgentTool with a more powerful alternative.
"""

from langchain_core.tools import Tool, StructuredTool
from typing import Any, Callable, Optional, Dict


# AgentTool is now just an alias for LangChain Tool
# This provides full compatibility with existing code
AgentTool = Tool


class MCPClientInitializationError(Exception):
    """
    Exception raised when MCP client initialization fails.

    This exception is raised when there are issues initializing or connecting
    to an MCP (Model Context Protocol) client.

    Example:
        >>> try:
        ...     client = MCPClient(config)
        ... except MCPClientInitializationError as e:
        ...     print(f"Failed to initialize MCP client: {e}")
    """

    pass


class MCPClient:
    """
    Wrapper for MCP (Model Context Protocol) client connections.

    This class wraps MCP client factories to provide a consistent interface
    for managing MCP server connections. It replaces the Strands MCPClient
    with a simpler, more flexible implementation.

    Attributes:
        client_factory: A callable that returns an MCP client instance
        _client: Cached client instance

    Example:
        >>> from mcp import stdio_client, StdioServerParameters
        >>> factory = lambda: stdio_client(StdioServerParameters(command="my-server"))
        >>> client = MCPClient(factory)
        >>> mcp_client = client.start()
        >>> tools = mcp_client.list_tools_sync()
    """

    def __init__(self, client_factory: Callable[[], Any]):
        """
        Initialize MCPClient with a client factory.

        Args:
            client_factory: A callable that returns an MCP client instance
        """
        self.client_factory = client_factory
        self._client = None

    def start(self) -> Any:
        """
        Start the MCP client and return it.

        Returns:
            The MCP client instance
        """
        if self._client is None:
            self._client = self.client_factory()
        return self._client

    def stop(self) -> None:
        """Stop the MCP client."""
        if self._client is not None:
            if hasattr(self._client, "close"):
                self._client.close()
            elif hasattr(self._client, "stop"):
                self._client.stop()
            self._client = None


def create_tool(
    name: str,
    description: str,
    func: Callable,
    args_schema: Optional[Dict[str, Any]] = None,
) -> Tool:
    """
    Create a LangChain tool from a function.

    This is a convenience function for creating tools that works with both
    simple functions and complex ones with schemas.

    Args:
        name: Name of the tool
        description: Description of what the tool does
        func: The function to wrap as a tool
        args_schema: Optional Pydantic model for argument validation

    Returns:
        A LangChain Tool instance

    Example:
        >>> def add(a: int, b: int) -> int:
        ...     '''Add two numbers'''
        ...     return a + b
        >>> tool = create_tool("add", "Add two numbers", add)
    """
    if args_schema:
        return StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema,
        )
    else:
        return StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
        )


def tool(
    name: str,
    description: str,
    inputSchema: Optional[Dict[str, Any]] = None,
    context: bool = False,
    **kwargs,
) -> Callable:
    """
    Decorator factory for creating tools.

    This is a decorator factory that creates a tool from a function.
    It replaces the Strands `tool` decorator with a LangChain-compatible version.

    Args:
        name: Name of the tool
        description: Description of what the tool does
        inputSchema: Optional JSON schema for input validation
        context: Whether to include context (ignored for compatibility)
        **kwargs: Additional arguments (ignored for compatibility)

    Returns:
        A decorator function that wraps a function as a tool

    Example:
        >>> @tool(name="add", description="Add two numbers")
        ... def add(a: int, b: int) -> int:
        ...     return a + b
    """

    def decorator(func: Callable) -> Tool:
        tool_obj = StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
        )
        # Add compatibility properties for Strands API
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(tool_obj, "tool_name", tool_obj.name)
        object.__setattr__(
            tool_obj,
            "tool_spec",
            {
                "name": tool_obj.name,
                "description": tool_obj.description,
            },
        )
        return tool_obj

    return decorator


def wrap_tool_for_compatibility(tool_obj: Tool) -> Tool:
    """
    Wrap a LangChain Tool to add Strands compatibility properties.

    This function adds the `tool_name` and `tool_spec` properties that
    Strands tools have, allowing existing code to work with LangChain tools.

    Args:
        tool_obj: A LangChain Tool instance

    Returns:
        The same tool object with added compatibility properties
    """
    if not hasattr(tool_obj, "tool_name"):
        object.__setattr__(tool_obj, "tool_name", tool_obj.name)
    if not hasattr(tool_obj, "tool_spec"):
        object.__setattr__(
            tool_obj,
            "tool_spec",
            {
                "name": tool_obj.name,
                "description": tool_obj.description,
            },
        )
    return tool_obj


__all__ = [
    "AgentTool",
    "MCPClient",
    "MCPClientInitializationError",
    "create_tool",
    "tool",
    "wrap_tool_for_compatibility",
]

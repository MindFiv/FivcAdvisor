"""
LangChain tool adapter for multi-provider tool support.

This module provides adapters to convert between Strands tool definitions
and LangChain tool definitions, maintaining compatibility with the existing
tool system while enabling LangChain integration.
"""

from typing import Any, Dict, Optional, List
from langchain_core.tools import Tool, StructuredTool


def convert_strands_tool_to_langchain(strands_tool: Any) -> Tool:
    """
    Convert a Strands AgentTool to a LangChain Tool.

    Args:
        strands_tool: A Strands AgentTool instance

    Returns:
        A LangChain Tool instance

    Raises:
        ValueError: If tool conversion fails
    """
    try:
        # Extract tool information from Strands tool
        tool_name = strands_tool.tool_name
        tool_spec = strands_tool.tool_spec
        description = tool_spec.get("description", "")

        # Get the tool function
        if hasattr(strands_tool, "func"):
            func = strands_tool.func
        elif callable(strands_tool):
            func = strands_tool
        else:
            raise ValueError(f"Tool {tool_name} is not callable")

        # Create LangChain tool wrapper using StructuredTool.from_function
        # This allows us to provide description even if function lacks docstring
        langchain_tool_instance = StructuredTool.from_function(
            func=func,
            name=tool_name,
            description=description or "Tool",
        )

        return langchain_tool_instance

    except Exception as e:
        raise ValueError(f"Failed to convert Strands tool to LangChain: {e}")


def convert_strands_tools_to_langchain(strands_tools: List[Any]) -> List[Tool]:
    """
    Convert a list of Strands AgentTools to LangChain Tools.

    Args:
        strands_tools: List of Strands AgentTool instances

    Returns:
        List of LangChain Tool instances
    """
    langchain_tools = []
    for tool in strands_tools:
        try:
            langchain_tool_instance = convert_strands_tool_to_langchain(tool)
            langchain_tools.append(langchain_tool_instance)
        except ValueError as e:
            print(f"Warning: {e}")
            continue

    return langchain_tools


def create_tool_adapter(
    strands_tool: Any,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Tool:
    """
    Create a LangChain tool adapter for a Strands tool.

    This function provides a flexible way to adapt Strands tools to LangChain,
    with optional name and description overrides.

    Args:
        strands_tool: A Strands AgentTool instance
        name: Optional override for tool name
        description: Optional override for tool description

    Returns:
        A LangChain Tool instance
    """
    # Convert the tool
    langchain_tool_instance = convert_strands_tool_to_langchain(strands_tool)

    # Apply overrides if provided
    if name:
        langchain_tool_instance.name = name
    if description:
        langchain_tool_instance.description = description

    return langchain_tool_instance


def is_strands_tool(obj: Any) -> bool:
    """
    Check if an object is a Strands AgentTool.

    Args:
        obj: Object to check

    Returns:
        True if object is a Strands AgentTool, False otherwise
    """
    try:
        return hasattr(obj, "tool_name") and hasattr(obj, "tool_spec")
    except Exception:
        return False


def is_langchain_tool(obj: Any) -> bool:
    """
    Check if an object is a LangChain Tool.

    Args:
        obj: Object to check

    Returns:
        True if object is a LangChain Tool, False otherwise
    """
    try:
        return isinstance(obj, Tool)
    except Exception:
        return False


class ToolAdapter:
    """
    Adapter for converting between Strands and LangChain tool formats.

    This class provides a unified interface for working with tools from
    both Strands and LangChain, automatically converting between formats
    as needed.
    """

    def __init__(self):
        """Initialize the tool adapter."""
        self._strands_to_langchain_cache: Dict[str, Tool] = {}

    def adapt(self, tool: Any) -> Tool:
        """
        Adapt a tool to LangChain format.

        If the tool is already a LangChain Tool, returns it as-is.
        If the tool is a Strands AgentTool, converts it to LangChain format.

        Args:
            tool: A tool in either Strands or LangChain format

        Returns:
            A LangChain Tool instance

        Raises:
            ValueError: If tool format is not recognized
        """
        if is_langchain_tool(tool):
            return tool
        elif is_strands_tool(tool):
            tool_name = tool.tool_name
            if tool_name not in self._strands_to_langchain_cache:
                self._strands_to_langchain_cache[tool_name] = (
                    convert_strands_tool_to_langchain(tool)
                )
            return self._strands_to_langchain_cache[tool_name]
        else:
            raise ValueError(f"Unknown tool format: {type(tool)}")

    def adapt_batch(self, tools: List[Any]) -> List[Tool]:
        """
        Adapt a batch of tools to LangChain format.

        Args:
            tools: List of tools in either Strands or LangChain format

        Returns:
            List of LangChain Tool instances
        """
        return [self.adapt(tool) for tool in tools]

    def clear_cache(self) -> None:
        """Clear the conversion cache."""
        self._strands_to_langchain_cache.clear()


# Global tool adapter instance
_tool_adapter = ToolAdapter()


def adapt_tool(tool: Any) -> Tool:
    """
    Adapt a tool to LangChain format using the global adapter.

    Args:
        tool: A tool in either Strands or LangChain format

    Returns:
        A LangChain Tool instance
    """
    return _tool_adapter.adapt(tool)


def adapt_tools(tools: List[Any]) -> List[Tool]:
    """
    Adapt a batch of tools to LangChain format using the global adapter.

    Args:
        tools: List of tools in either Strands or LangChain format

    Returns:
        List of LangChain Tool instances
    """
    return _tool_adapter.adapt_batch(tools)

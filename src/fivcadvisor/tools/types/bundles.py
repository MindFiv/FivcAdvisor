from typing import List

from langchain_core.tools import BaseTool, Tool


class ToolsBundle(Tool):
    """A bundle of tools from a single MCP server.

    ToolsBundle groups multiple tools together, typically from a single MCP (Model Context Protocol)
    server. It extends LangChain's Tool class and can be used with ToolsRetriever to manage
    collections of related tools.

    The bundle itself acts as a tool that returns all contained tools when called. This allows
    the bundle to be treated as a single entity in the retriever while still providing access
    to individual tools through the expand parameter.

    Attributes:
        name: The name of the bundle (typically the MCP server name)
        description: Concatenated descriptions of all tools in the bundle
        _tools: Internal storage for the list of tools (stored using object.__setattr__ to
                bypass Pydantic validation)

    Example:
        >>> tool1 = Tool(name="get_weather", description="Get weather info")
        >>> tool2 = Tool(name="get_time", description="Get current time")
        >>> bundle = ToolsBundle("weather_server", [tool1, tool2])
        >>> all_tools = bundle.get_all()
    """

    def __init__(self, name: str, tools: List[BaseTool]):
        """Initialize a ToolsBundle.

        Args:
            name: The name of the bundle (typically the MCP server name)
            tools: List of BaseTool instances to bundle together

        Raises:
            ValueError: If tools list is empty or any tool lacks a description
        """
        tools_desc = []
        for tool in tools:
            tool.handle_tool_error = True
            tools_desc.append(tool.description)

        description = "\n\n".join(tools_desc)
        description = f"Available Tools: \n\n {description}"
        super().__init__(name=name, func=self.get_all, description=description)
        # Store tools using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, "_tools", tools)

    def get_all(self) -> List[BaseTool]:
        """Return all tools in the bundle.

        Returns:
            List of all BaseTool instances in this bundle

        Note:
            Uses object.__getattribute__ to bypass Pydantic's attribute access mechanism
            and directly access the internal _tools storage.
        """
        return object.__getattribute__(self, "_tools")

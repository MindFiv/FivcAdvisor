"""
Tool Bundle Management System

This module provides a clean separation of concerns for managing tool bundles.
Tools from the same MCP client are grouped into bundles, allowing for
coordinated tool retrieval and expansion.
"""

from typing import List, Optional, Dict, Set, Callable, Any
from dataclasses import dataclass, field
from langchain_core.tools import Tool


@dataclass
class ToolsBundle:
    """
    Represents a bundle of related tools from the same MCP client.

    A bundle groups tools that work together and should be loaded together.
    For example, all tools from the 'playwright' MCP client form a bundle.

    Attributes:
        bundle_name: Unique identifier for this bundle (e.g., 'playwright', 'sequential-thinking')
        tools: Mapping of tool_name -> Tool
        metadata: Additional metadata about the bundle (e.g., client_name, version, description)
    """

    bundle_name: str
    """Unique identifier for this bundle"""

    tools: Dict[str, Tool] = field(default_factory=dict)
    """Mapping of tool_name -> Tool"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the bundle"""

    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool to this bundle.

        Args:
            tool: The Tool to add

        Raises:
            ValueError: If tool already exists in bundle
        """
        if tool.name in self.tools:
            raise ValueError(
                f"Tool {tool.name} already exists in bundle {self.bundle_name}"
            )
        self.tools[tool.name] = tool

    def add_tools(self, tools: List[Tool]) -> None:
        """
        Add multiple tools to this bundle.

        Args:
            tools: List of Tools to add
        """
        for tool in tools:
            self.add_tool(tool)

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name from this bundle.

        Args:
            tool_name: Name of the tool

        Returns:
            The Tool or None if not found
        """
        return self.tools.get(tool_name)

    def get_all_tools(self) -> List[Tool]:
        """
        Get all tools in this bundle.

        Returns:
            List of all Tools in this bundle
        """
        return list(self.tools.values())

    def get_tool_names(self) -> Set[str]:
        """
        Get all tool names in this bundle.

        Returns:
            Set of tool names
        """
        return set(self.tools.keys())

    def __len__(self) -> int:
        """Return the number of tools in this bundle."""
        return len(self.tools)

    def __repr__(self) -> str:
        return f"ToolsBundle(name={self.bundle_name}, tools={len(self.tools)})"


class ToolsBundleManager:
    """
    Manages tool bundles and provides operations on them.

    Responsibilities:
    - Register and manage tool bundles
    - Retrieve bundles by name
    - Expand tool lists to include related bundle tools
    - Query bundle information

    This class is completely independent of ToolsRetriever and can be
    tested and used separately.
    """

    def __init__(self):
        """Initialize the bundle manager."""
        self._bundles: Dict[str, ToolsBundle] = {}
        self._tool_to_bundle: Dict[str, str] = {}  # tool_name -> bundle_name mapping

    def create_bundle(
        self, bundle_name: str, metadata: Optional[Dict] = None
    ) -> ToolsBundle:
        """
        Create a new bundle.

        Args:
            bundle_name: Unique name for the bundle
            metadata: Optional metadata for the bundle

        Returns:
            The created ToolsBundle instance

        Raises:
            ValueError: If bundle already exists
        """
        if bundle_name in self._bundles:
            raise ValueError(f"Bundle '{bundle_name}' already exists")

        bundle = ToolsBundle(bundle_name=bundle_name, metadata=metadata or {})
        self._bundles[bundle_name] = bundle
        return bundle

    def add_bundle(self, bundle: ToolsBundle) -> None:
        """
        Register an existing bundle.

        Args:
            bundle: The ToolsBundle to register

        Raises:
            ValueError: If bundle name already exists
        """
        if bundle.bundle_name in self._bundles:
            raise ValueError(f"Bundle '{bundle.bundle_name}' already exists")

        self._bundles[bundle.bundle_name] = bundle

        # Update tool_to_bundle mapping
        for tool_name in bundle.get_tool_names():
            self._tool_to_bundle[tool_name] = bundle.bundle_name

    def add_tool_to_bundle(self, bundle_name: str, tool: Tool) -> None:
        """
        Add a tool to a bundle and update the mapping.

        Args:
            bundle_name: Name of the bundle
            tool: The Tool to add

        Raises:
            ValueError: If bundle doesn't exist
        """
        bundle = self.get_bundle(bundle_name)
        if bundle is None:
            raise ValueError(f"Bundle '{bundle_name}' does not exist")

        bundle.add_tool(tool)
        self._tool_to_bundle[tool.tool_name] = bundle_name

    def get_bundle(self, bundle_name: str) -> Optional[ToolsBundle]:
        """
        Get a bundle by name.

        Args:
            bundle_name: Name of the bundle

        Returns:
            The ToolsBundle or None if not found
        """
        return self._bundles.get(bundle_name)

    def get_bundle_by_tool(self, tool_name: str) -> Optional[ToolsBundle]:
        """
        Get the bundle that contains a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            The ToolsBundle containing the tool, or None if not found
        """
        bundle_name = self._tool_to_bundle.get(tool_name)
        if bundle_name:
            return self._bundles.get(bundle_name)
        return None

    def get_all_bundles(self) -> List[ToolsBundle]:
        """
        Get all registered bundles.

        Returns:
            List of all ToolsBundle instances
        """
        return list(self._bundles.values())

    def get_bundle_names(self) -> List[str]:
        """
        Get all bundle names.

        Returns:
            List of bundle names
        """
        return list(self._bundles.keys())

    def get_bundle_tools(self, bundle_name: str) -> List[Tool]:
        """
        Get all tools in a specific bundle.

        Args:
            bundle_name: Name of the bundle

        Returns:
            List of Tools in the bundle
        """
        bundle = self.get_bundle(bundle_name)
        if bundle:
            return bundle.get_all_tools()
        return []

    def expand_tools(
        self,
        tools: List[Tool],
        include_bundles: bool = True,
        bundle_filter: Optional[Callable[["ToolsBundle"], bool]] = None,
    ) -> List[Tool]:
        """
        Expand a list of tools to include related bundle tools.

        When a tool is found, this method can optionally include all other
        tools from the same bundle.

        Args:
            tools: List of tools to expand
            include_bundles: Whether to include other tools from the same bundle
            bundle_filter: Optional filter function to select which bundles to expand
                          Signature: (bundle: ToolsBundle) -> bool

        Returns:
            Expanded list of tools (may contain duplicates, caller should deduplicate)

        Example:
            >>> tools = [tool1, tool2]
            >>> expanded = manager.expand_tools(
            ...     tools,
            ...     bundle_filter=lambda b: b.bundle_name != "excluded_bundle"
            ... )
        """
        if not include_bundles:
            return tools

        expanded_tools = list(tools)
        expanded_tool_names = {t.name for t in tools}

        for tool in tools:
            bundle = self.get_bundle_by_tool(tool.name)
            if bundle is None:
                continue

            # Apply filter if provided
            if bundle_filter and not bundle_filter(bundle):
                continue

            # Add all tools from this bundle
            for bundle_tool in bundle.get_all_tools():
                if bundle_tool.name not in expanded_tool_names:
                    expanded_tools.append(bundle_tool)
                    expanded_tool_names.add(bundle_tool.name)

        return expanded_tools

    def get_bundle_info(self, bundle_name: str) -> Optional[Dict]:
        """
        Get information about a bundle.

        Args:
            bundle_name: Name of the bundle

        Returns:
            Dictionary with bundle info or None if not found
        """
        bundle = self.get_bundle(bundle_name)
        if not bundle:
            return None

        return {
            "name": bundle.bundle_name,
            "tool_count": len(bundle),
            "tool_names": list(bundle.get_tool_names()),
            "metadata": bundle.metadata,
        }

    def cleanup(self) -> None:
        """Clear all bundles."""
        self._bundles.clear()
        self._tool_to_bundle.clear()

    def __repr__(self) -> str:
        return f"ToolsBundleManager(bundles={len(self._bundles)})"

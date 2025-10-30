#!/usr/bin/env python3
"""
Tests for the ToolsBundle class.
"""

import pytest
from unittest.mock import Mock

from fivcadvisor.tools.types.bundles import ToolsBundle


class TestToolsBundle:
    """Test the ToolsBundle class."""

    def test_init_with_single_tool(self):
        """Test ToolsBundle initialization with a single tool."""
        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"

        bundle = ToolsBundle("test_bundle", [tool])

        assert bundle.name == "test_bundle"
        assert bundle.description is not None
        assert "A test tool" in bundle.description
        assert "Available Tools:" in bundle.description

    def test_init_with_multiple_tools(self):
        """Test ToolsBundle initialization with multiple tools."""
        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1 description"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2 description"

        bundle = ToolsBundle("test_bundle", [tool1, tool2])

        assert bundle.name == "test_bundle"
        assert "Tool 1 description" in bundle.description
        assert "Tool 2 description" in bundle.description

    def test_get_all_returns_tools(self):
        """Test that get_all() returns the tools in the bundle."""
        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        bundle = ToolsBundle("test_bundle", [tool1, tool2])

        tools = bundle.get_all()

        assert len(tools) == 2
        assert tool1 in tools
        assert tool2 in tools

    def test_bundle_is_baseTool(self):
        """Test that ToolsBundle is a BaseTool."""
        from langchain_core.tools import BaseTool

        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"

        bundle = ToolsBundle("test_bundle", [tool])

        assert isinstance(bundle, BaseTool)

    def test_bundle_has_name_attribute(self):
        """Test that ToolsBundle has a name attribute."""
        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"

        bundle = ToolsBundle("my_bundle", [tool])

        assert hasattr(bundle, "name")
        assert bundle.name == "my_bundle"

    def test_bundle_description_format(self):
        """Test that bundle description has correct format."""
        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "First tool"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Second tool"

        bundle = ToolsBundle("test_bundle", [tool1, tool2])

        # Description should start with "Available Tools:"
        assert bundle.description.startswith("Available Tools:")
        # Description should contain both tool descriptions
        assert "First tool" in bundle.description
        assert "Second tool" in bundle.description


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

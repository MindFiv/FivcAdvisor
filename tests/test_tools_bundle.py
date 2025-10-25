#!/usr/bin/env python3
"""
Tests for the tools bundle management system.
"""

import pytest
from unittest.mock import Mock

from fivcadvisor.tools.types.bundles import ToolsBundle, ToolsBundleManager


class TestToolsBundle:
    """Test the ToolsBundle class."""

    @pytest.fixture
    def mock_tool(self):
        """Create a mock tool."""
        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"
        return tool

    def test_bundle_creation(self):
        """Test creating a bundle."""
        bundle = ToolsBundle(bundle_name="test_bundle")

        assert bundle.bundle_name == "test_bundle"
        assert len(bundle) == 0
        assert bundle.get_tool_names() == set()

    def test_bundle_add_tool(self, mock_tool):
        """Test adding a tool to a bundle."""
        bundle = ToolsBundle(bundle_name="test_bundle")

        bundle.add_tool(mock_tool)

        assert len(bundle) == 1
        assert "test_tool" in bundle.get_tool_names()
        assert bundle.get_tool("test_tool") == mock_tool

    def test_bundle_add_duplicate_tool(self, mock_tool):
        """Test that adding duplicate tool raises ValueError."""
        bundle = ToolsBundle(bundle_name="test_bundle")
        bundle.add_tool(mock_tool)

        with pytest.raises(ValueError, match="already exists"):
            bundle.add_tool(mock_tool)

    def test_bundle_add_tools(self, mock_tool):
        """Test adding multiple tools to a bundle."""
        bundle = ToolsBundle(bundle_name="test_bundle")

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        bundle.add_tools([tool1, tool2])

        assert len(bundle) == 2
        assert "tool1" in bundle.get_tool_names()
        assert "tool2" in bundle.get_tool_names()

    def test_bundle_get_all_tools(self):
        """Test getting all tools from a bundle."""
        bundle = ToolsBundle(bundle_name="test_bundle")

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        bundle.add_tools([tool1, tool2])

        all_tools = bundle.get_all_tools()
        assert len(all_tools) == 2
        assert tool1 in all_tools
        assert tool2 in all_tools

    def test_bundle_metadata(self):
        """Test bundle metadata."""
        metadata = {"client_name": "playwright", "version": "1.0"}
        bundle = ToolsBundle(bundle_name="test_bundle", metadata=metadata)

        assert bundle.metadata == metadata


class TestToolsBundleManager:
    """Test the ToolsBundleManager class."""

    @pytest.fixture
    def manager(self):
        """Create a bundle manager."""
        return ToolsBundleManager()

    @pytest.fixture
    def mock_tool(self):
        """Create a mock tool."""
        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"
        return tool

    def test_manager_creation(self, manager):
        """Test creating a bundle manager."""
        assert len(manager.get_all_bundles()) == 0
        assert len(manager.get_bundle_names()) == 0

    def test_create_bundle(self, manager):
        """Test creating a bundle."""
        bundle = manager.create_bundle("test_bundle")

        assert bundle.bundle_name == "test_bundle"
        assert manager.get_bundle("test_bundle") == bundle

    def test_create_duplicate_bundle(self, manager):
        """Test that creating duplicate bundle raises ValueError."""
        manager.create_bundle("test_bundle")

        with pytest.raises(ValueError, match="already exists"):
            manager.create_bundle("test_bundle")

    def test_add_bundle(self, manager):
        """Test adding an existing bundle."""
        bundle = ToolsBundle(bundle_name="test_bundle")
        manager.add_bundle(bundle)

        assert manager.get_bundle("test_bundle") == bundle

    def test_get_bundle_by_tool(self, manager, mock_tool):
        """Test getting bundle by tool name."""
        bundle = manager.create_bundle("test_bundle")
        manager.add_tool_to_bundle("test_bundle", mock_tool)

        found_bundle = manager.get_bundle_by_tool("test_tool")
        assert found_bundle == bundle

    def test_get_bundle_tools(self, manager):
        """Test getting all tools in a bundle."""
        bundle = manager.create_bundle("test_bundle")

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        bundle.add_tools([tool1, tool2])

        tools = manager.get_bundle_tools("test_bundle")
        assert len(tools) == 2
        assert tool1 in tools
        assert tool2 in tools

    def test_expand_tools_without_bundles(self, manager, mock_tool):
        """Test expanding tools without bundle expansion."""
        tools = [mock_tool]
        expanded = manager.expand_tools(tools, include_bundles=False)

        assert len(expanded) == 1
        assert mock_tool in expanded

    def test_expand_tools_with_bundles(self, manager):
        """Test expanding tools with bundle expansion."""
        _ = manager.create_bundle("test_bundle")

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        tool3 = Mock()
        tool3.name = "tool3"
        tool3.description = "Tool 3"

        # Use manager's method to add tools and update mapping
        manager.add_tool_to_bundle("test_bundle", tool1)
        manager.add_tool_to_bundle("test_bundle", tool2)
        manager.add_tool_to_bundle("test_bundle", tool3)

        # Expand with only tool1
        expanded = manager.expand_tools([tool1], include_bundles=True)

        # Should include tool1 and all other tools from the bundle
        assert len(expanded) == 3
        assert tool1 in expanded
        assert tool2 in expanded
        assert tool3 in expanded

    def test_expand_tools_with_filter(self, manager):
        """Test expanding tools with bundle filter."""
        bundle1 = manager.create_bundle("bundle1")
        bundle2 = manager.create_bundle("bundle2")

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        tool3 = Mock()
        tool3.name = "tool3"
        tool3.description = "Tool 3"

        bundle1.add_tool(tool1)
        bundle2.add_tools([tool2, tool3])

        # Expand with filter that excludes bundle2
        def exclude_bundle2(bundle):
            return bundle.bundle_name != "bundle2"

        expanded = manager.expand_tools(
            [tool1], include_bundles=True, bundle_filter=exclude_bundle2
        )

        # Should only include tool1 (from bundle1)
        assert len(expanded) == 1
        assert tool1 in expanded

    def test_get_bundle_info(self, manager):
        """Test getting bundle information."""
        bundle = manager.create_bundle("test_bundle", metadata={"version": "1.0"})

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        bundle.add_tool(tool1)

        info = manager.get_bundle_info("test_bundle")

        assert info["name"] == "test_bundle"
        assert info["tool_count"] == 1
        assert "tool1" in info["tool_names"]
        assert info["metadata"]["version"] == "1.0"

    def test_cleanup(self, manager):
        """Test cleanup method."""
        manager.create_bundle("bundle1")
        manager.create_bundle("bundle2")

        manager.cleanup()

        assert len(manager.get_all_bundles()) == 0
        assert len(manager.get_bundle_names()) == 0


if __name__ == "__main__":
    pytest.main([__file__])

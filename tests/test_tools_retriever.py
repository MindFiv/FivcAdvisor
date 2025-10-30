#!/usr/bin/env python3
"""
Tests for the tools retriever module.
"""

import pytest
from unittest.mock import Mock

from fivcadvisor.tools.types.retrievers import ToolsRetriever
from fivcadvisor.tools.types.bundles import ToolsBundleManager


class TestToolsRetriever:
    """Test the ToolsRetriever class."""

    @pytest.fixture
    def mock_embedding_db(self):
        """Create a mock embedding database."""
        mock_db = Mock()
        mock_collection = Mock()
        mock_collection.clear = Mock()
        mock_collection.count = Mock(return_value=0)
        mock_collection.add = Mock()
        mock_collection.search = Mock(return_value=[])
        mock_db.get_collection = Mock(return_value=mock_collection)
        return mock_db

    @pytest.fixture
    def mock_tool(self):
        """Create a mock tool."""
        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"
        return tool

    def test_init(self, mock_embedding_db):
        """Test ToolsRetriever initialization."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        assert retriever.max_num == 10
        assert retriever.min_score == 0.0
        assert isinstance(retriever.tools, dict)
        assert len(retriever.tools) == 0
        assert isinstance(retriever.bundle_manager, ToolsBundleManager)
        mock_embedding_db.get_collection.assert_called_once_with("tools")

    def test_str(self, mock_embedding_db):
        """Test string representation."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        assert str(retriever) == "ToolsRetriever(num_tools=0)"

    def test_cleanup(self, mock_embedding_db):
        """Test cleanup method."""
        retriever = ToolsRetriever(db=mock_embedding_db)
        retriever.tools["tool1"] = Mock()
        retriever.max_num = 5
        retriever.min_score = 0.5

        retriever.cleanup()

        assert retriever.max_num == 10
        assert retriever.min_score == 0.0
        assert len(retriever.tools) == 0
        assert retriever.collection.clear.call_count >= 1

    def test_add_tool(self, mock_embedding_db, mock_tool):
        """Test adding a tool."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        retriever.add(mock_tool)

        assert "test_tool" in retriever.tools
        assert retriever.tools["test_tool"] == mock_tool
        retriever.collection.add.assert_called_once()

    def test_add_duplicate_tool(self, mock_embedding_db, mock_tool):
        """Test that adding duplicate tool raises ValueError."""
        retriever = ToolsRetriever(db=mock_embedding_db)
        retriever.add(mock_tool)

        with pytest.raises(ValueError, match="Duplicate tool name"):
            retriever.add(mock_tool)

    def test_add_tool_without_description(self, mock_embedding_db):
        """Test that adding tool without description raises ValueError."""
        retriever = ToolsRetriever(db=mock_embedding_db)
        tool = Mock()
        tool.name = "bad_tool"
        tool.description = ""

        with pytest.raises(ValueError, match="Tool description is empty"):
            retriever.add(tool)

    def test_add_batch(self, mock_embedding_db):
        """Test adding multiple tools."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        retriever.add_batch([tool1, tool2])

        assert len(retriever.tools) == 2
        assert "tool1" in retriever.tools
        assert "tool2" in retriever.tools

    def test_get_tool(self, mock_embedding_db, mock_tool):
        """Test getting a tool by name."""
        retriever = ToolsRetriever(db=mock_embedding_db)
        retriever.add(mock_tool)

        result = retriever.get("test_tool")

        assert result == mock_tool

    def test_get_nonexistent_tool(self, mock_embedding_db):
        """Test getting a nonexistent tool returns None."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        result = retriever.get("nonexistent")

        assert result is None

    def test_get_batch(self, mock_embedding_db):
        """Test getting multiple tools."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        retriever.add_batch([tool1, tool2])

        results = retriever.get_batch(["tool1", "tool2"])

        assert len(results) == 2
        assert results[0] == tool1
        assert results[1] == tool2

    def test_get_all(self, mock_embedding_db):
        """Test getting all tools."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        retriever.add_batch([tool1, tool2])

        results = retriever.get_all()

        assert len(results) == 2
        assert tool1 in results
        assert tool2 in results

    def test_retrieve_min_score_property(self, mock_embedding_db):
        """Test retrieve_min_score property."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        assert retriever.retrieve_min_score == 0.0

        retriever.retrieve_min_score = 0.5

        assert retriever.retrieve_min_score == 0.5
        assert retriever.min_score == 0.5

    def test_retrieve_max_num_property(self, mock_embedding_db):
        """Test retrieve_max_num property."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        assert retriever.retrieve_max_num == 10

        retriever.retrieve_max_num = 20

        assert retriever.retrieve_max_num == 20
        assert retriever.max_num == 20

    def test_retrieve(self, mock_embedding_db):
        """Test retrieving tools by query."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool1 = Mock()
        tool1.name = "calculator"
        tool1.description = "Calculate math"

        tool2 = Mock()
        tool2.name = "search"
        tool2.description = "Search the web"

        retriever.add_batch([tool1, tool2])

        # Mock search results - score should be at top level
        retriever.collection.search = Mock(
            return_value=[
                {
                    "text": "Calculate math",
                    "metadata": {"__tool__": "calculator"},
                    "score": 0.9,
                },
                {
                    "text": "Search the web",
                    "metadata": {"__tool__": "search"},
                    "score": 0.7,
                },
            ]
        )

        results = retriever.retrieve("math calculation")

        assert len(results) == 2
        assert tool1 in results
        assert tool2 in results

    def test_retrieve_with_min_score(self, mock_embedding_db):
        """Test retrieving tools with minimum score filter."""
        retriever = ToolsRetriever(db=mock_embedding_db)
        retriever.retrieve_min_score = 0.8

        tool1 = Mock()
        tool1.name = "calculator"
        tool1.description = "Calculate math"

        tool2 = Mock()
        tool2.name = "search"
        tool2.description = "Search the web"

        retriever.add_batch([tool1, tool2])

        # Mock search results with different scores - score should be at top level
        retriever.collection.search = Mock(
            return_value=[
                {
                    "text": "Calculate math",
                    "metadata": {"__tool__": "calculator"},
                    "score": 0.9,
                },
                {
                    "text": "Search the web",
                    "metadata": {"__tool__": "search"},
                    "score": 0.7,
                },
            ]
        )

        results = retriever.retrieve("math calculation")

        # Only calculator should be returned (score >= 0.8)
        assert len(results) == 1
        assert tool1 in results
        assert tool2 not in results

    def test_call(self, mock_embedding_db):
        """Test calling retriever as a function."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool1 = Mock()
        tool1.name = "calculator"
        tool1.description = "Calculate math"

        retriever.add(tool1)

        # Mock search results - score should be at top level
        retriever.collection.search = Mock(
            return_value=[
                {
                    "text": "Calculate math",
                    "metadata": {"__tool__": "calculator"},
                    "score": 0.9,
                },
            ]
        )

        results = retriever("math calculation")

        assert len(results) == 1
        assert results[0]["name"] == "calculator"
        assert results[0]["description"] == "Calculate math"

    def test_add_with_bundle(self, mock_embedding_db, mock_tool):
        """Test adding a tool with bundle."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        retriever.add(mock_tool, tool_bundle="test_bundle")

        assert "test_tool" in retriever.tools
        assert retriever.bundle_manager.get_bundle("test_bundle") is not None
        bundle = retriever.bundle_manager.get_bundle("test_bundle")
        assert "test_tool" in bundle.get_tool_names()

    def test_add_batch_with_bundle(self, mock_embedding_db):
        """Test adding multiple tools to the same bundle."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2"

        retriever.add_batch([tool1, tool2], tool_bundle="test_bundle")

        assert len(retriever.tools) == 2
        bundle = retriever.bundle_manager.get_bundle("test_bundle")
        assert len(bundle) == 2
        assert "tool1" in bundle.get_tool_names()
        assert "tool2" in bundle.get_tool_names()

    def test_to_tool(self, mock_embedding_db):
        """Test converting retriever to a tool."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool = retriever.to_tool()

        assert tool is not None
        assert hasattr(tool, "name")
        # LangChain tools have invoke method instead of being directly callable
        assert hasattr(tool, "invoke")

    def test_remove_tool(self, mock_embedding_db):
        """Test removing a tool."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"

        retriever.add(tool)
        assert "test_tool" in retriever.tools

        # Mock the collection.get() to return documents with the tool's metadata
        mock_embedding_db.get_collection.return_value.collection.get = Mock(
            return_value={
                "ids": ["id1", "id2"],
                "metadatas": [
                    {"__tool__": "test_tool"},
                    {"__tool__": "test_tool"},
                ],
            }
        )

        retriever.remove("test_tool")

        assert "test_tool" not in retriever.tools
        # Verify delete was called on the collection
        mock_embedding_db.get_collection.return_value.collection.delete.assert_called_once_with(
            ids=["id1", "id2"]
        )

    def test_remove_nonexistent_tool(self, mock_embedding_db):
        """Test removing a nonexistent tool raises ValueError."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        with pytest.raises(ValueError, match="Tool not found"):
            retriever.remove("nonexistent")

    def test_remove_tool_from_bundle(self, mock_embedding_db):
        """Test removing a tool that's in a bundle."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"

        retriever.add(tool, tool_bundle="test_bundle")

        # Verify tool is in bundle
        bundle = retriever.bundle_manager.get_bundle("test_bundle")
        assert "test_tool" in bundle.get_tool_names()

        # Mock the collection.get() to return documents
        mock_embedding_db.get_collection.return_value.collection.get = Mock(
            return_value={
                "ids": ["id1"],
                "metadatas": [{"__tool__": "test_tool"}],
            }
        )

        retriever.remove("test_tool")

        # Verify tool is removed from bundle
        assert "test_tool" not in bundle.get_tool_names()
        # Verify tool_to_bundle mapping is updated
        assert retriever.bundle_manager.get_bundle_by_tool("test_tool") is None

    def test_remove_tool_with_no_embedding_docs(self, mock_embedding_db):
        """Test removing a tool that has no embedding documents."""
        retriever = ToolsRetriever(db=mock_embedding_db)

        tool = Mock()
        tool.name = "test_tool"
        tool.description = "A test tool"

        retriever.add(tool)

        # Mock the collection.get() to return no matching documents
        mock_embedding_db.get_collection.return_value.collection.get = Mock(
            return_value={
                "ids": ["id1"],
                "metadatas": [{"__tool__": "other_tool"}],
            }
        )

        retriever.remove("test_tool")

        assert "test_tool" not in retriever.tools
        # delete should not be called if no matching docs
        mock_embedding_db.get_collection.return_value.collection.delete.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])

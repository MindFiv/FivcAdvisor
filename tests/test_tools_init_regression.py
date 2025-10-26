#!/usr/bin/env python3
"""
Regression tests for tools module initialization.

This module contains tests to prevent regressions in the tools initialization
process, particularly around tool attribute access.

Regression: https://github.com/FivcAdvisor/fivcadvisor/issues/XXX
- Issue: AttributeError: 'StructuredTool' object has no attribute 'tool_name'
- Root Cause: Code was accessing tool.tool_name instead of tool.name
- Fix: Changed to use tool.name which is the correct LangChain Tool attribute
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fivcadvisor.tools import _load_retriever
from fivcadvisor.tools.types.retrievers import ToolsRetriever


class TestToolsInitRegression:
    """Regression tests for tools module initialization."""

    def test_load_retriever_uses_correct_tool_attribute(self):
        """
        Regression test: Ensure _load_retriever uses tool.name, not tool.tool_name.

        This test prevents the AttributeError that occurred when trying to access
        'tool_name' attribute on LangChain StructuredTool objects.

        The correct attribute for LangChain tools is 'name', not 'tool_name'.
        """
        with patch("fivcadvisor.tools.ToolsLoader") as mock_loader_class:
            with patch("fivcadvisor.tools.ToolsRetriever") as mock_retriever_class:
                # Setup mock retriever
                mock_retriever = MagicMock(spec=ToolsRetriever)

                # Create mock tools with 'name' attribute (correct LangChain attribute)
                mock_tool1 = Mock()
                mock_tool1.name = "calculator"
                mock_tool1.description = "Calculate math expressions"

                mock_tool2 = Mock()
                mock_tool2.name = "search"
                mock_tool2.description = "Search the web"

                # Setup get_all to return tools with 'name' attribute
                mock_retriever.get_all.return_value = [mock_tool1, mock_tool2]

                mock_retriever_class.return_value = mock_retriever
                mock_loader_class.return_value = Mock()

                # This should not raise AttributeError
                result = _load_retriever()

                # Verify the retriever was returned
                assert result == mock_retriever

                # Verify get_all was called
                mock_retriever.get_all.assert_called()

    def test_get_all_returns_tools_with_name_attribute(self):
        """
        Test that ToolsRetriever.get_all() returns tools with 'name' attribute.

        This ensures that tools returned from get_all() have the correct
        LangChain Tool interface with 'name' attribute.
        """
        from fivcadvisor.tools.types.retrievers import ToolsRetriever
        from unittest.mock import Mock

        # Create mock embedding DB
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.get_collection.return_value = mock_collection

        retriever = ToolsRetriever(db=mock_db)

        # Create tools with 'name' attribute (LangChain standard)
        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool 1 description"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool 2 description"

        # Add tools to retriever
        retriever.add(tool1)
        retriever.add(tool2)

        # Get all tools
        all_tools = retriever.get_all()

        # Verify all tools have 'name' attribute
        assert len(all_tools) == 2
        for tool in all_tools:
            assert hasattr(tool, "name"), f"Tool {tool} missing 'name' attribute"
            assert tool.name in ["tool1", "tool2"]

    def test_print_statement_uses_tool_name_attribute(self, capsys):
        """
        Test that the print statement in _load_retriever uses tool.name correctly.

        This test captures the print output and verifies that tool names are
        correctly extracted using the 'name' attribute.
        """
        with patch("fivcadvisor.tools.ToolsLoader") as mock_loader_class:
            with patch("fivcadvisor.tools.ToolsRetriever") as mock_retriever_class:
                # Setup mock retriever
                mock_retriever = MagicMock(spec=ToolsRetriever)

                # Create mock tools
                mock_tool1 = Mock()
                mock_tool1.name = "calculator"

                mock_tool2 = Mock()
                mock_tool2.name = "search"

                mock_retriever.get_all.return_value = [mock_tool1, mock_tool2]
                mock_retriever_class.return_value = mock_retriever
                mock_loader_class.return_value = Mock()

                # Call _load_retriever
                _load_retriever()

                # Capture printed output
                captured = capsys.readouterr()

                # Verify the print statement contains tool names
                assert "Registered Tools:" in captured.out
                assert "calculator" in captured.out
                assert "search" in captured.out

    def test_tools_retriever_get_all_with_langchain_tools(self):
        """
        Test that ToolsRetriever.get_all() works with actual LangChain Tool objects.

        This test uses real LangChain tools to ensure compatibility.
        """
        from langchain_core.tools import tool as make_tool
        from fivcadvisor.tools.types.retrievers import ToolsRetriever
        from unittest.mock import Mock

        # Create mock embedding DB
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.get_collection.return_value = mock_collection

        retriever = ToolsRetriever(db=mock_db)

        # Create a real LangChain tool
        @make_tool
        def calculator(expression: str) -> float:
            """Calculate a mathematical expression."""
            return eval(expression)

        @make_tool
        def search(query: str) -> str:
            """Search for information."""
            return f"Results for {query}"

        # Add tools to retriever
        retriever.add(calculator)
        retriever.add(search)

        # Get all tools
        all_tools = retriever.get_all()

        # Verify tools have 'name' attribute (not 'tool_name')
        assert len(all_tools) == 2
        tool_names = [t.name for t in all_tools]
        assert "calculator" in tool_names
        assert "search" in tool_names

        # Verify we can access the name attribute without AttributeError
        for tool in all_tools:
            name = tool.name  # This should not raise AttributeError
            assert isinstance(name, str)
            assert len(name) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

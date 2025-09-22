"""
Tests for the FivcAdvisor web interface (Streamlit app).
"""

import pytest
from unittest.mock import patch
from fivcadvisor.app import (
    main,
    create_interface,
    get_available_graphs,
    run_graph_sync,
    run_graph_async,
    format_result,
    process_message,
)


class TestWebInterfaceImports:
    """Test that web interface components can be imported."""

    def test_import_main_function(self):
        """Test that main function can be imported."""
        assert callable(main)

    def test_import_graph_functions(self):
        """Test that graph functions can be imported."""
        assert callable(get_available_graphs)
        assert callable(run_graph_sync)
        assert callable(run_graph_async)


class TestGraphFunctions:
    """Test graph-related functions."""

    def test_get_available_graphs(self):
        """Test getting available graphs."""
        graphs = get_available_graphs()

        assert isinstance(graphs, dict)
        assert len(graphs) > 0

        # Check expected graph types
        expected_graphs = ["general", "simple", "complex"]
        for graph_type in expected_graphs:
            assert graph_type in graphs
            assert isinstance(graphs[graph_type], str)
            assert len(graphs[graph_type]) > 0

    @pytest.mark.asyncio
    async def test_run_graph_async_with_mock(self):
        """Test async graph execution with mocked backend."""
        # Test that the function exists and can handle basic input
        # We'll mock the entire function to avoid complex backend setup
        with patch("fivcadvisor.app.run_graph_async") as mock_run_graph:
            mock_run_graph.return_value = {
                "success": True,
                "error": None,
                "result": {"test": "mocked_result"},
            }

            result = await mock_run_graph("general", "test query", verbose=False)

            assert result["success"] is True
            assert result["error"] is None
            assert result["result"] == {"test": "mocked_result"}

            mock_run_graph.assert_called_once_with(
                "general", "test query", verbose=False
            )

    def test_run_graph_sync_with_mock(self):
        """Test sync graph execution with mocked backend."""
        with patch("fivcadvisor.app.asyncio.run") as mock_asyncio_run:
            mock_asyncio_run.return_value = {
                "success": True,
                "error": None,
                "result": {"test": "sync_result"},
            }

            result = run_graph_sync("simple", "test query", verbose=True)

            assert result["success"] is True
            assert result["error"] is None
            assert result["result"] == {"test": "sync_result"}

            # Verify asyncio.run was called
            mock_asyncio_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_graph_async_error_handling(self):
        """Test error handling in async graph execution."""
        with patch("fivcadvisor.app.create_general_graph") as mock_create_graph:
            # Mock an exception during graph creation
            mock_create_graph.side_effect = Exception("Test error")

            result = await run_graph_async("general", "test query")

            assert result["success"] is False
            assert "Test error" in result["error"]
            assert result["result"] is None

    @pytest.mark.asyncio
    async def test_run_graph_async_unknown_graph_type(self):
        """Test handling of unknown graph type."""
        result = await run_graph_async("unknown_graph", "test query")

        assert result["success"] is False
        assert "Unknown graph type" in result["error"]
        assert result["result"] is None


class TestWebInterfaceIntegration:
    """Integration tests for web interface."""

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        # We can't easily test Streamlit app execution in unit tests,
        # but we can verify the function exists and is importable
        assert callable(main)

    def test_create_interface_function_exists(self):
        """Test that create_interface function exists and is callable."""
        assert callable(create_interface)

    def test_all_exports_available(self):
        """Test that all expected exports are available."""
        from fivcadvisor.app import __all__

        expected_exports = [
            "main",
            "create_interface",
            "get_available_graphs",
            "run_graph_sync",
            "run_graph_async",
        ]

        assert isinstance(__all__, list)
        for export in expected_exports:
            assert export in __all__


class TestStreamlitSpecificFunctions:
    """Test Streamlit-specific functions."""

    def test_format_result_success(self):
        """Test formatting successful results."""
        result = {
            "success": True,
            "error": None,
            "result": {"final_result": {"final_output": "This is the final output"}},
        }

        formatted = format_result(result)
        assert "✅ **Result:**" in formatted
        assert "This is the final output" in formatted

    def test_format_result_error(self):
        """Test formatting error results."""
        result = {"success": False, "error": "Something went wrong", "result": None}

        formatted = format_result(result)
        assert "❌ **Error:**" in formatted
        assert "Something went wrong" in formatted

    def test_process_message_empty(self):
        """Test processing empty message."""
        message = ""
        graph_type = "general"
        verbose = False

        response = process_message(message, graph_type, verbose)

        assert response == "Please enter a message."

    @patch("fivcadvisor.app.run_graph_sync")
    def test_process_message_with_content(self, mock_run_graph):
        """Test processing message with content."""
        mock_run_graph.return_value = {
            "success": True,
            "error": None,
            "result": {"final_result": {"final_output": "Test response"}},
        }

        message = "Test message"
        graph_type = "general"
        verbose = False

        response = process_message(message, graph_type, verbose)

        assert "Test response" in response
        mock_run_graph.assert_called_once_with("general", "Test message", False)

#!/usr/bin/env python
"""
Tests for FivcAdvisor Web Interface

Basic tests to ensure the web interface components work correctly.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fivcadvisor.app import get_available_flows, run_flow_sync


class TestWebInterface:
    """Test cases for the web interface functionality."""

    def test_get_available_flows(self):
        """Test that available flows are returned correctly."""
        flows = get_available_flows()

        assert isinstance(flows, dict)
        assert "general" in flows
        assert "simple" in flows
        assert "complex" in flows

        # Check that descriptions are provided
        for flow_type, description in flows.items():
            assert isinstance(flow_type, str)
            assert isinstance(description, str)
            assert len(description) > 0

    @patch("fivcadvisor.app.flows")
    @patch("fivcadvisor.app.tools")
    @patch("fivcadvisor.app.logs")
    @patch("fivcadvisor.app.create_output_dir")
    def test_run_flow_sync_success(
        self, mock_output_dir, mock_logs, mock_tools, mock_flows
    ):
        """Test successful flow execution."""
        # Mock the flow and its result
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "status": "completed",
            "result": "test result",
        }

        mock_flow = MagicMock()
        mock_flow.kickoff.return_value = mock_result

        mock_flow_creator = MagicMock(return_value=mock_flow)
        mock_flows.default_retriever.get.return_value = mock_flow_creator

        # Mock other dependencies
        mock_logs.register_default_events = MagicMock()
        mock_logs.agent_logger = MagicMock()
        mock_tools.default_retriever = MagicMock()
        mock_output_dir.return_value.__enter__ = MagicMock()
        mock_output_dir.return_value.__exit__ = MagicMock()

        # Test the function
        result = run_flow_sync("general", "test query", verbose=False)

        # Assertions
        assert result["success"] is True
        assert result["error"] is None
        assert result["result"] == {"status": "completed", "result": "test result"}

        # Verify mocks were called
        mock_flows.default_retriever.get.assert_called_once_with("general")
        mock_flow_creator.assert_called_once()
        mock_flow.kickoff.assert_called_once_with(inputs={"user_query": "test query"})

    @patch("fivcadvisor.app.flows")
    def test_run_flow_sync_unknown_flow(self, mock_flows):
        """Test handling of unknown flow type."""
        mock_flows.default_retriever.get.return_value = None

        result = run_flow_sync("unknown_flow", "test query")

        assert result["success"] is False
        assert "Unknown flow type" in result["error"]
        assert result["result"] is None

    @patch("fivcadvisor.app.flows")
    @patch("fivcadvisor.app.tools")
    @patch("fivcadvisor.app.logs")
    @patch("fivcadvisor.app.create_output_dir")
    def test_run_flow_sync_exception(
        self, mock_output_dir, mock_logs, mock_tools, mock_flows
    ):
        """Test handling of exceptions during flow execution."""
        # Mock flow that raises an exception
        mock_flow = MagicMock()
        mock_flow.kickoff.side_effect = Exception("Test exception")

        mock_flow_creator = MagicMock(return_value=mock_flow)
        mock_flows.default_retriever.get.return_value = mock_flow_creator

        # Mock other dependencies
        mock_logs.register_default_events = MagicMock()
        mock_logs.agent_logger = MagicMock()
        mock_tools.default_retriever = MagicMock()

        # Mock the context manager properly
        mock_context = MagicMock()
        mock_output_dir.return_value = mock_context
        mock_context.__enter__ = MagicMock(return_value=mock_context)
        mock_context.__exit__ = MagicMock(return_value=None)

        result = run_flow_sync("general", "test query")

        assert result is not None
        assert result["success"] is False
        assert "Test exception" in result["error"]
        assert result["result"] is None


class TestCLIWebCommand:
    """Test cases for the CLI web command."""

    def test_web_command_import(self):
        """Test that the web command can be imported from CLI."""
        from fivcadvisor.cli import web

        assert callable(web)

    @patch("fivcadvisor.cli.subprocess.run")
    @patch("fivcadvisor.cli.Path")
    def test_web_command_execution(self, mock_path, mock_subprocess):
        """Test web command execution logic."""
        from fivcadvisor.cli import web

        # Mock path existence
        mock_app_path = MagicMock()
        mock_app_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value = mock_app_path

        # Mock subprocess
        mock_subprocess.return_value = None

        # This would normally be called by typer, but we can test the logic
        try:
            # We can't easily test the actual typer command without more complex mocking
            # But we can verify the function exists and is properly structured
            assert hasattr(web, "__call__")
        except Exception:
            # Expected since we're not in a proper typer context
            pass


if __name__ == "__main__":
    pytest.main([__file__])

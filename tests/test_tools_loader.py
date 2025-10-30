#!/usr/bin/env python3
"""
Tests for the tools/types/loaders module.

This module contains tests for the ToolsLoader class which manages loading
tools from MCP servers and registering them with a ToolsRetriever.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fivcadvisor.tools.types.loaders import ToolsLoader
from fivcadvisor.tools.types.retrievers import ToolsRetriever


class TestToolsLoaderInit:
    """Test ToolsLoader initialization."""

    def test_init_with_retriever(self):
        """Test initialization with a ToolsRetriever."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test_server:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            assert loader.tools_retriever == mock_retriever
            assert loader.tools_bundles == {}
            assert loader.config is not None
        finally:
            os.unlink(config_path)

    def test_init_without_retriever_raises_assertion(self):
        """Test that initialization without retriever raises AssertionError."""
        with pytest.raises(AssertionError):
            ToolsLoader(tools_retriever=None)

    def test_init_with_default_config_file(self):
        """Test initialization with default config file from environment."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "mcp.yaml")
            with open(config_path, "w") as f:
                f.write("test_server:\n  command: python\n  args:\n    - test.py\n")

            # Set environment variable
            old_env = os.environ.get("MCP_FILE")
            try:
                os.environ["MCP_FILE"] = config_path
                loader = ToolsLoader(tools_retriever=mock_retriever)
                assert loader.config is not None
            finally:
                if old_env is not None:
                    os.environ["MCP_FILE"] = old_env
                else:
                    os.environ.pop("MCP_FILE", None)


class TestToolsLoaderLoad:
    """Test ToolsLoader load methods."""

    def test_load_calls_load_async(self):
        """Test that load() calls load_async()."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test_server:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            with patch.object(
                loader, "load_async", new_callable=AsyncMock
            ) as mock_load_async:
                loader.load()
                mock_load_async.assert_called_once()
        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_load_async_with_no_servers(self):
        """Test load_async with no configured servers."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")  # Empty config
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            with patch(
                "fivcadvisor.tools.types.loaders.MultiServerMCPClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_client.connections = {}
                mock_client_class.return_value = mock_client

                await loader.load_async()

                # Should not call add_batch if no servers
                mock_retriever.add_batch.assert_not_called()
        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_load_async_with_tools(self):
        """Test load_async successfully loads tools."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test_server:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            # Create mock tools
            mock_tool1 = Mock()
            mock_tool1.name = "tool1"
            mock_tool2 = Mock()
            mock_tool2.name = "tool2"

            with patch(
                "fivcadvisor.tools.types.loaders.MultiServerMCPClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_session = AsyncMock()
                mock_session.__aenter__.return_value = mock_session
                mock_session.__aexit__.return_value = None

                mock_client.connections = {"test_server": Mock()}
                mock_client.session.return_value = mock_session
                mock_client_class.return_value = mock_client

                with patch(
                    "fivcadvisor.tools.types.loaders.load_mcp_tools",
                    new_callable=AsyncMock,
                ) as mock_load_tools:
                    mock_load_tools.return_value = [mock_tool1, mock_tool2]

                    await loader.load_async()

                    # Verify tools were added
                    mock_retriever.add_batch.assert_called_once()
                    call_args = mock_retriever.add_batch.call_args
                    assert call_args[0][0] == [mock_tool1, mock_tool2]
                    assert call_args[1]["tool_bundle"] == "test_server"

                    # Verify tools_bundles was updated
                    assert "test_server" in loader.tools_bundles
                    assert "tool1" in loader.tools_bundles["test_server"]
                    assert "tool2" in loader.tools_bundles["test_server"]
        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_load_async_handles_errors(self):
        """Test load_async handles errors gracefully."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test_server:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            with patch(
                "fivcadvisor.tools.types.loaders.MultiServerMCPClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_client.connections = {"test_server": Mock()}
                mock_client.session.side_effect = Exception("Connection failed")
                mock_client_class.return_value = mock_client

                # Should not raise, just continue
                await loader.load_async()

                # Should not call add_batch if error occurred
                mock_retriever.add_batch.assert_not_called()
        finally:
            os.unlink(config_path)


class TestToolsLoaderCleanup:
    """Test ToolsLoader cleanup method."""

    def test_cleanup_removes_all_tools(self):
        """Test cleanup removes all tracked tools."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test_server:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            # Simulate tools being loaded in bundles
            loader.tools_bundles = {
                "bundle1": {"tool1", "tool2"},
                "bundle2": {"tool3"}
            }

            loader.cleanup()

            # Verify remove was called for each tool
            assert mock_retriever.remove.call_count == 3

            # Verify tools_bundles was cleared
            assert loader.tools_bundles == {}
        finally:
            os.unlink(config_path)

    def test_cleanup_with_no_tools(self):
        """Test cleanup with no tools loaded."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test_server:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            loader.cleanup()

            # Should not call remove if no tools
            mock_retriever.remove.assert_not_called()
        finally:
            os.unlink(config_path)

    def test_cleanup_calls_remove_method(self):
        """Test that cleanup uses the remove() method (not delete())."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test_server:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )
            loader.tools_bundles = {"bundle1": {"tool1"}}

            loader.cleanup()

            # Verify remove method was called (not delete)
            mock_retriever.remove.assert_called_once_with("tool1")
        finally:
            os.unlink(config_path)


class TestToolsLoaderIncrementalUpdates:
    """Test ToolsLoader incremental bundle updates."""

    @pytest.mark.asyncio
    async def test_load_async_adds_new_bundles(self):
        """Test load_async adds new bundles."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("server1:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            # Create mock tools
            mock_tool1 = Mock()
            mock_tool1.name = "tool1"

            with patch(
                "fivcadvisor.tools.types.loaders.MultiServerMCPClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_session = AsyncMock()
                mock_session.__aenter__.return_value = mock_session
                mock_session.__aexit__.return_value = None

                mock_client.connections = {"server1": Mock()}
                mock_client.session.return_value = mock_session
                mock_client_class.return_value = mock_client

                with patch(
                    "fivcadvisor.tools.types.loaders.load_mcp_tools",
                    new_callable=AsyncMock,
                ) as mock_load_tools:
                    mock_load_tools.return_value = [mock_tool1]

                    await loader.load_async()

                    # Verify bundle was added
                    assert "server1" in loader.tools_bundles
                    assert "tool1" in loader.tools_bundles["server1"]
        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_load_async_removes_old_bundles(self):
        """Test load_async removes bundles that are no longer configured."""
        mock_retriever = Mock(spec=ToolsRetriever)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("server1:\n  command: python\n  args:\n    - test.py\n")
            f.flush()
            config_path = f.name

        try:
            loader = ToolsLoader(
                tools_retriever=mock_retriever, config_file=config_path
            )

            # Simulate previously loaded bundle
            loader.tools_bundles = {"old_server": {"old_tool"}}

            with patch(
                "fivcadvisor.tools.types.loaders.MultiServerMCPClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_session = AsyncMock()
                mock_session.__aenter__.return_value = mock_session
                mock_session.__aexit__.return_value = None

                # Only server1 is now available
                mock_client.connections = {"server1": Mock()}
                mock_client.session.return_value = mock_session
                mock_client_class.return_value = mock_client

                with patch(
                    "fivcadvisor.tools.types.loaders.load_mcp_tools",
                    new_callable=AsyncMock,
                ) as mock_load_tools:
                    mock_load_tools.return_value = []

                    await loader.load_async()

                    # Verify old bundle was removed
                    mock_retriever.remove.assert_called_once_with("old_tool")
                    assert "old_server" not in loader.tools_bundles
                    # server1 won't be in tools_bundles if no tools were loaded
        finally:
            os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__])

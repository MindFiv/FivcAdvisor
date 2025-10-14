#!/usr/bin/env python3
"""
Tests for ChatManager functionality.

Tests the chat manager for handling conversation state and agent execution:
- Initialization with tools retriever
- Session and agent ID management with caching
- History listing
- Query execution with callbacks
- Cleanup functionality
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fivcadvisor.app.managers import ChatManager
from fivcadvisor.agents.types import AgentsRuntime, AgentsStatus
from fivcadvisor import tools


class TestChatManagerInitialization:
    """Test ChatManager initialization."""

    def test_init_with_tools_retriever(self):
        """Test creating ChatManager with tools retriever."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        manager = ChatManager(tools_retriever=mock_retriever)

        assert manager.tools_retriever is mock_retriever
        assert manager.runtime_repo is not None
        assert manager.monitor_manager is not None
        assert manager.running is False

    def test_init_without_tools_retriever_raises_error(self):
        """Test that initialization without tools retriever raises assertion error."""
        with pytest.raises(AssertionError):
            ChatManager(tools_retriever=None)

    def test_is_running_property(self):
        """Test is_running property reflects running state."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        manager = ChatManager(tools_retriever=mock_retriever)

        assert manager.is_running is False

        manager.running = True
        assert manager.is_running is True

        manager.running = False
        assert manager.is_running is False


class TestChatManagerSessionManagement:
    """Test session and agent ID management."""

    @patch("fivcadvisor.app.managers.chat.utils.OutputDir")
    @patch("fivcadvisor.app.managers.chat.settings.SettingsConfig")
    def test_session_id_creation(self, mock_settings_config, mock_output_dir):
        """Test session_id is created and persisted when not exists."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        mock_config = Mock()
        mock_config.get.return_value = None  # No existing session_id
        mock_settings_config.return_value = mock_config

        manager = ChatManager(tools_retriever=mock_retriever)
        session_id = manager.session_id

        # Verify session_id was created
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) == 36  # UUID format

        # Verify it was saved
        mock_config.set.assert_called_once_with("session_id", session_id)
        mock_config.save.assert_called_once()

    @patch("fivcadvisor.app.managers.chat.utils.OutputDir")
    @patch("fivcadvisor.app.managers.chat.settings.SettingsConfig")
    def test_session_id_retrieval(self, mock_settings_config, mock_output_dir):
        """Test session_id is retrieved from config when exists."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        existing_id = "existing-session-id"
        mock_config = Mock()
        mock_config.get.return_value = existing_id
        mock_settings_config.return_value = mock_config

        manager = ChatManager(tools_retriever=mock_retriever)
        session_id = manager.session_id

        assert session_id == existing_id
        mock_config.set.assert_not_called()

    @patch("fivcadvisor.app.managers.chat.utils.OutputDir")
    @patch("fivcadvisor.app.managers.chat.settings.SettingsConfig")
    def test_session_id_caching(self, mock_settings_config, mock_output_dir):
        """Test session_id is cached after first access."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        mock_config = Mock()
        mock_config.get.return_value = "test-session-id"
        mock_settings_config.return_value = mock_config

        manager = ChatManager(tools_retriever=mock_retriever)

        # Access session_id multiple times
        id1 = manager.session_id
        id2 = manager.session_id
        id3 = manager.session_id

        # Should be the same instance
        assert id1 == id2 == id3

        # Config should only be accessed once due to caching
        assert mock_settings_config.call_count == 1

    @patch("fivcadvisor.app.managers.chat.utils.OutputDir")
    @patch("fivcadvisor.app.managers.chat.settings.SettingsConfig")
    def test_agent_id_creation(self, mock_settings_config, mock_output_dir):
        """Test agent_id is created and persisted when not exists."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        mock_config = Mock()
        mock_config.get.return_value = None  # No existing agent_id
        mock_settings_config.return_value = mock_config

        manager = ChatManager(tools_retriever=mock_retriever)
        agent_id = manager.agent_id

        # Verify agent_id was created
        assert agent_id is not None
        assert isinstance(agent_id, str)
        assert len(agent_id) == 36  # UUID format

        # Verify it was saved
        mock_config.set.assert_called_with("agent_id", agent_id)
        mock_config.save.assert_called()

    @patch("fivcadvisor.app.managers.chat.utils.OutputDir")
    @patch("fivcadvisor.app.managers.chat.settings.SettingsConfig")
    def test_agent_id_caching(self, mock_settings_config, mock_output_dir):
        """Test agent_id is cached after first access."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        mock_config = Mock()
        mock_config.get.return_value = "test-agent-id"
        mock_settings_config.return_value = mock_config

        manager = ChatManager(tools_retriever=mock_retriever)

        # Access agent_id multiple times
        id1 = manager.agent_id
        id2 = manager.agent_id

        # Should be the same instance
        assert id1 == id2

        # Config should only be accessed once due to caching
        assert mock_settings_config.call_count == 1


class TestChatManagerHistory:
    """Test history listing functionality."""

    def test_list_history_returns_completed_runtimes(self):
        """Test list_history returns only completed agent runtimes."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        manager = ChatManager(tools_retriever=mock_retriever)

        # Mock runtime repository
        completed_runtime = AgentsRuntime(
            agent_id="test-agent",
            status=AgentsStatus.COMPLETED,
        )
        pending_runtime = AgentsRuntime(
            agent_id="test-agent",
            status=AgentsStatus.EXECUTING,
        )

        manager.runtime_repo.list_agent_runtimes = Mock(
            return_value=[completed_runtime, pending_runtime]
        )

        # Mock agent_id to avoid config access
        with patch.object(manager, "agent_id", "test-agent"):
            history = manager.list_history()

        # Should only return completed runtime
        assert len(history) == 1
        assert history[0] is completed_runtime
        assert history[0].is_completed is True

    def test_list_history_empty(self):
        """Test list_history returns empty list when no history."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        manager = ChatManager(tools_retriever=mock_retriever)

        manager.runtime_repo.list_agent_runtimes = Mock(return_value=[])

        with patch.object(manager, "agent_id", "test-agent"):
            history = manager.list_history()

        assert history == []


class TestChatManagerAsk:
    """Test query execution functionality."""

    @pytest.mark.asyncio
    async def test_ask_basic_execution(self):
        """Test basic ask execution flow."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        manager = ChatManager(tools_retriever=mock_retriever)

        # Mock the agent runtime
        mock_agent = AsyncMock()
        mock_agent.invoke_async = AsyncMock(return_value="test response")

        manager.monitor_manager.create_agent_runtime = Mock(return_value=mock_agent)

        with patch.object(manager, "agent_id", "test-agent"):
            result = await manager.ask("test query")

        assert result == "test response"
        assert manager.running is False  # Should be reset after execution
        mock_agent.invoke_async.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_ask_with_callback(self):
        """Test ask execution with on_event callback."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        manager = ChatManager(tools_retriever=mock_retriever)

        mock_callback = Mock()
        mock_agent = AsyncMock()
        mock_agent.invoke_async = AsyncMock(return_value="response")

        manager.monitor_manager.create_agent_runtime = Mock(return_value=mock_agent)

        with patch.object(manager, "agent_id", "test-agent"):
            await manager.ask("query", on_event=mock_callback)

        # Verify callback was passed to create_agent_runtime
        call_kwargs = manager.monitor_manager.create_agent_runtime.call_args[1]
        assert call_kwargs["on_event"] is mock_callback

    @pytest.mark.asyncio
    async def test_ask_raises_error_when_already_running(self):
        """Test ask raises ValueError when agent is already running."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        manager = ChatManager(tools_retriever=mock_retriever)
        manager.running = True

        with pytest.raises(ValueError) as exc_info:
            await manager.ask("test query")

        assert "already processing" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_ask_resets_running_on_exception(self):
        """Test ask resets running flag even when exception occurs."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        manager = ChatManager(tools_retriever=mock_retriever)

        mock_agent = AsyncMock()
        mock_agent.invoke_async = AsyncMock(side_effect=Exception("Test error"))

        manager.monitor_manager.create_agent_runtime = Mock(return_value=mock_agent)

        with patch.object(manager, "agent_id", "test-agent"):
            with pytest.raises(Exception):
                await manager.ask("query")

        # Running should be reset even after exception
        assert manager.running is False


class TestChatManagerCleanup:
    """Test cleanup functionality."""

    @patch("fivcadvisor.app.managers.chat.utils.OutputDir")
    @patch("fivcadvisor.app.managers.chat.settings.SettingsConfig")
    def test_cleanup_clears_cached_ids(self, mock_settings_config, mock_output_dir):
        """Test cleanup clears cached session_id and agent_id."""
        mock_retriever = Mock(spec=tools.ToolsRetriever)
        mock_config = Mock()
        mock_config.get.return_value = "test-id"
        mock_settings_config.return_value = mock_config

        manager = ChatManager(tools_retriever=mock_retriever)

        # Access IDs to cache them
        old_session_id = manager.session_id
        old_agent_id = manager.agent_id

        # Clear the mock to track new calls
        mock_settings_config.reset_mock()
        mock_config.get.return_value = None  # Return None for new IDs

        # Cleanup
        manager.cleanup()

        # Access IDs again - should create new ones
        new_session_id = manager.session_id
        new_agent_id = manager.agent_id

        # Should have created new IDs
        assert new_session_id != old_session_id
        assert new_agent_id != old_agent_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

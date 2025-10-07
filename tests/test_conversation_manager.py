#!/usr/bin/env python3
"""
Tests for the ToolFilteringConversationManager.
"""

import pytest
from unittest.mock import Mock
from strands.agent import Agent, SlidingWindowConversationManager
from fivcadvisor.agents.types.conversations import ToolFilteringConversationManager


class TestToolFilteringConversationManager:
    """Test the ToolFilteringConversationManager class."""

    def test_init(self):
        """Test initialization with a wrapped conversation manager."""
        wrapped_manager = SlidingWindowConversationManager(window_size=40)
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        assert manager.conversation_manager is wrapped_manager
        assert manager.removed_message_count == 0

    def test_get_state_basic(self):
        """Test get_state returns correct structure."""
        wrapped_manager = SlidingWindowConversationManager(window_size=40)
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        state = manager.get_state()

        # Check the structure
        assert "__name__" in state
        assert state["__name__"] == "ToolFilteringConversationManager"
        assert "removed_message_count" in state
        assert state["removed_message_count"] == 0
        assert "wrapped_manager_state" in state
        assert "wrapped_manager_class" in state
        assert "wrapped_manager_init_params" in state

    def test_get_state_with_sliding_window(self):
        """Test get_state captures SlidingWindowConversationManager parameters."""
        wrapped_manager = SlidingWindowConversationManager(
            window_size=50, should_truncate_results=False
        )
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        state = manager.get_state()

        # Check wrapped manager info
        assert state["wrapped_manager_class"] == "SlidingWindowConversationManager"
        assert state["wrapped_manager_init_params"]["window_size"] == 50
        assert state["wrapped_manager_init_params"]["should_truncate_results"] is False

    def test_get_state_preserves_removed_count(self):
        """Test get_state preserves removed_message_count."""
        wrapped_manager = SlidingWindowConversationManager(window_size=40)
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        # Manually set removed_message_count
        manager.removed_message_count = 5

        state = manager.get_state()
        assert state["removed_message_count"] == 5

    def test_restore_from_session_basic(self):
        """Test restore_from_session restores state correctly."""
        wrapped_manager = SlidingWindowConversationManager(window_size=40)
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        # Create a state
        state = {
            "__name__": "ToolFilteringConversationManager",
            "removed_message_count": 10,
            "wrapped_manager_state": {
                "__name__": "SlidingWindowConversationManager",
                "removed_message_count": 5,
            },
        }

        result = manager.restore_from_session(state)

        # Check restoration
        assert manager.removed_message_count == 10
        assert manager.conversation_manager.removed_message_count == 5
        assert result is None  # Default behavior

    def test_restore_from_session_invalid_class(self):
        """Test restore_from_session raises error for invalid class name."""
        wrapped_manager = SlidingWindowConversationManager(window_size=40)
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        # Create a state with wrong class name
        state = {
            "__name__": "WrongClassName",
            "removed_message_count": 10,
        }

        with pytest.raises(ValueError) as exc_info:
            manager.restore_from_session(state)

        assert "Invalid conversation manager state" in str(exc_info.value)
        assert "ToolFilteringConversationManager" in str(exc_info.value)

    def test_restore_from_session_without_wrapped_state(self):
        """Test restore_from_session handles missing wrapped_manager_state."""
        wrapped_manager = SlidingWindowConversationManager(window_size=40)
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        # Create a state without wrapped_manager_state
        state = {
            "__name__": "ToolFilteringConversationManager",
            "removed_message_count": 10,
        }

        result = manager.restore_from_session(state)

        # Should still restore own state
        assert manager.removed_message_count == 10
        assert result is None

    def test_serialization_round_trip(self):
        """Test full serialization and deserialization cycle."""
        # Create initial manager
        wrapped_manager = SlidingWindowConversationManager(
            window_size=50, should_truncate_results=False
        )
        manager1 = ToolFilteringConversationManager(
            conversation_manager=wrapped_manager
        )
        manager1.removed_message_count = 15
        manager1.conversation_manager.removed_message_count = 8

        # Serialize
        state = manager1.get_state()

        # Create new manager and restore
        wrapped_manager2 = SlidingWindowConversationManager(
            window_size=50, should_truncate_results=False
        )
        manager2 = ToolFilteringConversationManager(
            conversation_manager=wrapped_manager2
        )
        manager2.restore_from_session(state)

        # Verify state is preserved
        assert manager2.removed_message_count == 15
        assert manager2.conversation_manager.removed_message_count == 8

    def test_get_state_is_json_serializable(self):
        """Test that get_state returns JSON-serializable data."""
        import json

        wrapped_manager = SlidingWindowConversationManager(window_size=40)
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)
        manager.removed_message_count = 5

        state = manager.get_state()

        # Should not raise an exception
        json_str = json.dumps(state)
        restored_state = json.loads(json_str)

        # Verify data integrity
        assert restored_state["__name__"] == "ToolFilteringConversationManager"
        assert restored_state["removed_message_count"] == 5

    def test_apply_management_filters_tool_blocks(self):
        """Test that apply_management filters out toolUse and toolResult blocks."""
        wrapped_manager = SlidingWindowConversationManager(window_size=40)
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        # Create a mock agent with messages containing tool blocks
        agent = Mock(spec=Agent)
        agent.messages = [
            {
                "role": "user",
                "content": [{"text": "Hello"}],
            },
            {
                "role": "assistant",
                "content": [
                    {"text": "Let me help you"},
                    {"toolUse": {"toolUseId": "123", "name": "test_tool"}},
                ],
            },
            {
                "role": "user",
                "content": [
                    {"toolResult": {"toolUseId": "123", "content": "result"}},
                ],
            },
        ]

        manager.apply_management(agent, max_tokens=1000)

        # Check that tool blocks are filtered
        assert (
            len(agent.messages) == 2
        )  # Third message should be removed (no content after filtering)
        assert len(agent.messages[1]["content"]) == 1  # Only text block remains
        assert "text" in agent.messages[1]["content"][0]
        assert "toolUse" not in str(agent.messages[1]["content"])

    def test_reduce_context_delegates_to_wrapped_manager(self):
        """Test that reduce_context delegates to the wrapped manager."""
        wrapped_manager = Mock(spec=SlidingWindowConversationManager)
        wrapped_manager.reduce_context = Mock()
        manager = ToolFilteringConversationManager(conversation_manager=wrapped_manager)

        agent = Mock(spec=Agent)
        agent.messages = [{"role": "user", "content": [{"text": "test"}]}]
        exception = Exception("Test exception")

        manager.reduce_context(agent, exception)

        # Verify delegation
        wrapped_manager.reduce_context.assert_called_once_with(agent, exception)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

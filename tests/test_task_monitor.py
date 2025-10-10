#!/usr/bin/env python3
"""
Tests for TaskMonitor functionality.
"""

from unittest.mock import Mock
from datetime import datetime

from fivcadvisor.tasks.types import TaskMonitor, TaskRuntimeStep, TaskStatus


class TestTaskTrace:
    """Tests for TaskRuntimeStep class"""

    def test_initialization(self):
        """Test TaskRuntimeStep initialization"""
        event = TaskRuntimeStep(
            id="test-123",
            agent_name="TestAgent",
        )

        assert event.agent_name == "TestAgent"
        assert event.id == "test-123"
        assert event.agent_id == "test-123"  # computed field
        assert event.status == TaskStatus.PENDING
        assert event.started_at is None
        assert event.completed_at is None
        assert event.messages == []
        assert event.error is None

    def test_duration_calculation(self):
        """Test duration calculation"""
        event = TaskRuntimeStep(agent_name="TestAgent")

        # No duration when not started
        assert event.duration is None

        # Set start and end times
        event.started_at = datetime(2024, 1, 1, 12, 0, 0)
        event.completed_at = datetime(2024, 1, 1, 12, 0, 5)

        # Should calculate 5 seconds
        assert event.duration == 5.0

    def test_is_running(self):
        """Test is_running property"""
        event = TaskRuntimeStep(agent_name="TestAgent")

        assert not event.is_running

        event.status = TaskStatus.EXECUTING
        assert event.is_running

        event.status = TaskStatus.COMPLETED
        assert not event.is_running

    def test_is_completed(self):
        """Test is_completed property"""
        event = TaskRuntimeStep(agent_name="TestAgent")

        assert not event.is_completed

        event.status = TaskStatus.EXECUTING
        assert not event.is_completed

        event.status = TaskStatus.COMPLETED
        assert event.is_completed

        event.status = TaskStatus.FAILED
        assert event.is_completed

    def test_model_dump(self):
        """Test Pydantic model_dump"""
        event = TaskRuntimeStep(
            id="test-123",
            agent_name="TestAgent",
        )
        event.status = TaskStatus.EXECUTING
        event.started_at = datetime(2024, 1, 1, 12, 0, 0)
        from strands.types.content import Message

        event.messages.append(Message(role="user", content="test"))

        # Test with messages included (default)
        result = event.model_dump(mode="json")

        assert result["agent_name"] == "TestAgent"
        assert result["id"] == "test-123"
        assert result["agent_id"] == "test-123"  # computed field
        assert result["status"] == "executing"  # TaskStatus.EXECUTING value
        assert result["started_at"] == "2024-01-01T12:00:00"
        assert "messages" in result
        assert len(result["messages"]) == 1

        # Test without messages (compact mode)
        result_compact = event.model_dump(mode="json", exclude={"messages"})
        assert "messages" not in result_compact


class TestTaskMonitor:
    """Tests for TaskMonitor class"""

    def test_initialization(self):
        """Test TaskMonitor initialization"""
        monitor = TaskMonitor()

        assert monitor._on_event is None
        assert monitor.list_steps() == []

    def test_initialization_with_callbacks(self):
        """Test TaskMonitor initialization with callbacks"""
        on_event = Mock()

        monitor = TaskMonitor(on_event=on_event)

        assert monitor._on_event == on_event

    def test_callback_handler(self):
        """Test callback handler is callable (deprecated)"""
        monitor = TaskMonitor()

        # Monitor should be callable (deprecated but still works)
        assert callable(monitor)

    def test_agent_start(self):
        """Test agent start event handling"""
        on_event = Mock()
        monitor = TaskMonitor(on_event=on_event)

        # Create mock agent
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"
        mock_agent.messages = []

        # Trigger start event using deprecated __call__ method
        monitor(mock_agent)

        # Verify event was created
        event = monitor.get_step("test-123")
        assert event is not None
        assert event.agent_name == "TestAgent"
        assert event.agent_id == "test-123"
        assert event.status == TaskStatus.EXECUTING
        assert event.started_at is not None

        # Verify callback was called
        assert on_event.called

    def test_completion_success(self):
        """Test completion event handling (success)"""
        on_event = Mock()
        monitor = TaskMonitor(on_event=on_event)

        # Setup: create an event first
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"
        mock_agent.messages = []

        monitor(mock_agent)

        # Trigger completion event using deprecated __call__ method
        monitor(mock_agent, result="test result")

        # Verify event was updated
        event = monitor.get_step("test-123")
        assert event.status == TaskStatus.COMPLETED
        assert event.completed_at is not None
        assert event.error is None

    def test_completion_failure(self):
        """Test completion event handling (failure)"""
        monitor = TaskMonitor()

        # Setup: create an event first
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"
        mock_agent.messages = []

        monitor(mock_agent)

        # Trigger completion event with error using deprecated __call__ method
        monitor(mock_agent, error=Exception("Test error"))

        # Verify event was updated
        event = monitor.get_step("test-123")
        assert event.status == TaskStatus.FAILED
        assert event.error == "Test error"

    def test_message_added(self):
        """Test message added event handling"""
        monitor = TaskMonitor()

        # Setup: create an event first
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"
        mock_agent.messages = []

        monitor(mock_agent)

        # Create message event
        from strands.types.content import Message

        message = Message(role="user", content="test")

        # Trigger message event using deprecated __call__ method
        monitor(mock_agent, message=message)

        # Verify message was stored
        event = monitor.get_step("test-123")
        assert len(event.messages) == 1
        assert event.messages[0] == message

    def test_list_events(self):
        """Test listing events"""
        monitor = TaskMonitor()

        # Create multiple events using deprecated __call__ method
        for i in range(3):
            mock_agent = Mock()
            mock_agent.name = f"Agent{i}"
            mock_agent.agent_id = f"id-{i}"
            mock_agent.messages = []

            monitor(mock_agent)

        # Get all events
        events = monitor.list_steps()
        assert len(events) == 3

        # Verify all agents are present
        agent_names = {e.agent_name for e in events}
        assert agent_names == {"Agent0", "Agent1", "Agent2"}

    def test_get_event_by_agent_id(self):
        """Test getting event by agent_id"""
        monitor = TaskMonitor()

        # Create multiple events using deprecated __call__ method
        for i in range(3):
            mock_agent = Mock()
            mock_agent.name = f"Agent{i}"
            mock_agent.agent_id = f"id-{i}"
            mock_agent.messages = []

            monitor(mock_agent)

        # Get specific event
        event = monitor.get_step("id-1")
        assert event is not None
        assert event.agent_name == "Agent1"
        assert event.agent_id == "id-1"

        # Non-existent ID
        event = monitor.get_step("non-existent")
        assert event is None

    def test_cleanup(self):
        """Test cleanup events"""
        monitor = TaskMonitor()

        # Create some events using deprecated __call__ method
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"
        mock_agent.messages = []

        monitor(mock_agent)

        assert len(monitor.list_steps()) == 1

        # Clear events
        monitor.cleanup()

        assert len(monitor.list_steps()) == 0

        # Test clearing specific agent
        mock_agent1 = Mock()
        mock_agent1.name = "Agent1"
        mock_agent1.agent_id = "id-1"
        mock_agent1.messages = []

        mock_agent2 = Mock()
        mock_agent2.name = "Agent2"
        mock_agent2.agent_id = "id-2"
        mock_agent2.messages = []

        monitor(mock_agent1)
        monitor(mock_agent2)

        assert len(monitor.list_steps()) == 2

        # Clear only one agent
        monitor.cleanup(step_id="id-1")
        assert len(monitor.list_steps()) == 1
        assert monitor.get_step("id-1") is None
        assert monitor.get_step("id-2") is not None

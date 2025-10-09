#!/usr/bin/env python3
"""
Tests for TaskTracer functionality.
"""

from unittest.mock import Mock
from datetime import datetime

from fivcadvisor.tasks.types import TaskTracer, TaskEvent, TaskStatus


class TestTaskEvent:
    """Tests for TaskEvent class"""

    def test_initialization(self):
        """Test TaskEvent initialization"""
        event = TaskEvent(
            agent_name="TestAgent",
            agent_id="test-123",
            query="test query",
        )

        assert event.agent_name == "TestAgent"
        assert event.agent_id == "test-123"
        assert event.query == "test query"
        assert event.status == TaskStatus.IDLE
        assert event.started_at is None
        assert event.completed_at is None
        assert event.messages == []
        assert event.error is None
        assert event.result is None

    def test_duration_calculation(self):
        """Test duration calculation"""
        event = TaskEvent(agent_name="TestAgent")

        # No duration when not started
        assert event.duration is None

        # Set start and end times
        event.started_at = datetime(2024, 1, 1, 12, 0, 0)
        event.completed_at = datetime(2024, 1, 1, 12, 0, 5)

        # Should calculate 5 seconds
        assert event.duration == 5.0

    def test_is_running(self):
        """Test is_running property"""
        event = TaskEvent(agent_name="TestAgent")

        assert not event.is_running

        event.status = TaskStatus.RUNNING
        assert event.is_running

        event.status = TaskStatus.COMPLETED
        assert not event.is_running

    def test_is_completed(self):
        """Test is_completed property"""
        event = TaskEvent(agent_name="TestAgent")

        assert not event.is_completed

        event.status = TaskStatus.RUNNING
        assert not event.is_completed

        event.status = TaskStatus.COMPLETED
        assert event.is_completed

        event.status = TaskStatus.FAILED
        assert event.is_completed

    def test_model_dump(self):
        """Test Pydantic model_dump"""
        event = TaskEvent(
            agent_name="TestAgent",
            agent_id="test-123",
            query="test query",
        )
        event.status = TaskStatus.RUNNING
        event.started_at = datetime(2024, 1, 1, 12, 0, 0)
        event.messages.append({"role": "user", "content": "test"})

        # Test with messages included (default)
        result = event.model_dump(mode="json")

        assert result["agent_name"] == "TestAgent"
        assert result["agent_id"] == "test-123"
        assert result["query"] == "test query"
        assert result["status"] == "running"
        assert result["started_at"] == "2024-01-01T12:00:00"
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert "result" in result

        # Test without messages (compact mode)
        result_compact = event.model_dump(mode="json", exclude={"messages"})
        assert "messages" not in result_compact


class TestTaskTracer:
    """Tests for TaskTracer class"""

    def test_initialization(self):
        """Test TaskTracer initialization"""
        tracer = TaskTracer()

        assert tracer.on_event is None
        assert tracer.list_events() == []

    def test_initialization_with_callbacks(self):
        """Test TaskTracer initialization with callbacks"""
        on_event = Mock()

        tracer = TaskTracer(on_event=on_event)

        assert tracer.on_event == on_event

    def test_callback_handler(self):
        """Test callback handler is callable"""
        tracer = TaskTracer()

        # Tracer should be callable
        assert callable(tracer)

    def test_agent_start(self):
        """Test agent start event handling"""
        on_event = Mock()
        tracer = TaskTracer(on_event=on_event)

        # Create mock agent
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"

        # Trigger start event
        tracer(mock_agent, query="test query")

        # Verify event was created
        event = tracer.get_event("test-123")
        assert event is not None
        assert event.agent_name == "TestAgent"
        assert event.agent_id == "test-123"
        assert event.query == "test query"
        assert event.status == TaskStatus.RUNNING
        assert event.started_at is not None

        # Verify callback was called
        assert on_event.called

    def test_completion_success(self):
        """Test completion event handling (success)"""
        on_event = Mock()
        tracer = TaskTracer(on_event=on_event)

        # Setup: create an event first
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"

        tracer(mock_agent, query="test query")

        # Trigger completion event
        tracer(mock_agent, result="test result")

        # Verify event was updated
        event = tracer.get_event("test-123")
        assert event.status == TaskStatus.COMPLETED
        assert event.completed_at is not None
        assert event.result == "test result"
        assert event.error is None

    def test_completion_failure(self):
        """Test completion event handling (failure)"""
        tracer = TaskTracer()

        # Setup: create an event first
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"

        tracer(mock_agent, query="test query")

        # Trigger completion event with error
        tracer(mock_agent, error=Exception("Test error"))

        # Verify event was updated
        event = tracer.get_event("test-123")
        assert event.status == TaskStatus.FAILED
        assert event.error == "Test error"

    def test_message_added(self):
        """Test message added event handling"""
        tracer = TaskTracer()

        # Setup: create an event first
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"

        tracer(mock_agent, query="test query")

        # Create message event
        message = {"role": "user", "content": [{"text": "test"}]}

        # Trigger message event
        tracer(mock_agent, message=message)

        # Verify message was stored
        event = tracer.get_event("test-123")
        assert len(event.messages) == 1
        assert event.messages[0] == message

    def test_list_events(self):
        """Test listing events"""
        tracer = TaskTracer()

        # Create multiple events
        for i in range(3):
            mock_agent = Mock()
            mock_agent.name = f"Agent{i}"
            mock_agent.agent_id = f"id-{i}"

            tracer(mock_agent, query=f"query {i}")

        # Get all events
        events = tracer.list_events()
        assert len(events) == 3

        # Verify all agents are present
        agent_names = {e.agent_name for e in events}
        assert agent_names == {"Agent0", "Agent1", "Agent2"}

    def test_get_event_by_agent_id(self):
        """Test getting event by agent_id"""
        tracer = TaskTracer()

        # Create multiple events
        for i in range(3):
            mock_agent = Mock()
            mock_agent.name = f"Agent{i}"
            mock_agent.agent_id = f"id-{i}"

            tracer(mock_agent, query=f"query {i}")

        # Get specific event
        event = tracer.get_event("id-1")
        assert event is not None
        assert event.agent_name == "Agent1"
        assert event.agent_id == "id-1"

        # Non-existent ID
        event = tracer.get_event("non-existent")
        assert event is None

    def test_cleanup(self):
        """Test cleanup events"""
        tracer = TaskTracer()

        # Create some events
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_id = "test-123"

        tracer(mock_agent, query="test query")

        assert len(tracer.list_events()) == 1

        # Clear events
        tracer.cleanup()

        assert len(tracer.list_events()) == 0

        # Test clearing specific agent
        mock_agent1 = Mock()
        mock_agent1.name = "Agent1"
        mock_agent1.agent_id = "id-1"

        mock_agent2 = Mock()
        mock_agent2.name = "Agent2"
        mock_agent2.agent_id = "id-2"

        tracer(mock_agent1, query="query 1")
        tracer(mock_agent2, query="query 2")

        assert len(tracer.list_events()) == 2

        # Clear only one agent
        tracer.cleanup(agent_id="id-1")
        assert len(tracer.list_events()) == 1
        assert tracer.get_event("id-1") is None
        assert tracer.get_event("id-2") is not None

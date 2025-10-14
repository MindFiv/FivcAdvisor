"""
Unit tests for AgentsRuntime and AgentsRuntimeToolCall models.

Tests the agent runtime data models including:
- AgentsRuntimeToolCall creation and computed fields
- AgentsRuntime creation and computed fields
- Status tracking
- Tool call tracking
- Timing calculations
"""

from datetime import datetime
from fivcadvisor.agents.types import (
    AgentsRuntime,
    AgentsRuntimeToolCall,
    AgentsStatus,
)


class TestAgentsRuntimeToolCall:
    """Test AgentsRuntimeToolCall model."""

    def test_create_tool_call(self):
        """Test creating a tool call record."""
        tool_call = AgentsRuntimeToolCall(
            tool_use_id="test-123",
            tool_name="calculator",
            tool_input={"expression": "2+2"},
        )

        assert tool_call.id == "test-123"  # id is computed from tool_use_id
        assert tool_call.tool_use_id == "test-123"
        assert tool_call.tool_name == "calculator"
        assert tool_call.tool_input == {"expression": "2+2"}
        assert tool_call.status == "pending"
        assert tool_call.tool_result is None
        assert tool_call.error is None

    def test_tool_call_with_result(self):
        """Test tool call with result."""
        tool_call = AgentsRuntimeToolCall(
            tool_use_id="test-123",
            tool_name="calculator",
            tool_input={"expression": "2+2"},
            tool_result="4",
            status="success",
        )

        assert tool_call.tool_result == "4"
        assert tool_call.status == "success"
        assert tool_call.is_completed is True

    def test_tool_call_with_error(self):
        """Test tool call with error."""
        tool_call = AgentsRuntimeToolCall(
            tool_use_id="test-123",
            tool_name="calculator",
            tool_input={"expression": "invalid"},
            status="error",
            error="Invalid expression",
        )

        assert tool_call.status == "error"
        assert tool_call.error == "Invalid expression"
        assert tool_call.is_completed is True

    def test_tool_call_duration(self):
        """Test tool call duration calculation."""
        start = datetime(2024, 1, 1, 12, 0, 0)
        end = datetime(2024, 1, 1, 12, 0, 5)

        tool_call = AgentsRuntimeToolCall(
            tool_use_id="test-123",
            tool_name="calculator",
            tool_input={},
            started_at=start,
            completed_at=end,
        )

        assert tool_call.duration == 5.0

    def test_tool_call_duration_none_when_incomplete(self):
        """Test duration is None when tool call is incomplete."""
        tool_call = AgentsRuntimeToolCall(
            tool_use_id="test-123",
            tool_name="calculator",
            tool_input={},
            started_at=datetime.now(),
        )

        assert tool_call.duration is None

    def test_tool_call_id_computed_field(self):
        """Test that id is a computed field that returns tool_use_id."""
        tool_call = AgentsRuntimeToolCall(
            tool_use_id="unique-tool-call-id",
            tool_name="calculator",
            tool_input={},
        )

        # id should always equal tool_use_id
        assert tool_call.id == tool_call.tool_use_id
        assert tool_call.id == "unique-tool-call-id"


class TestAgentsRuntime:
    """Test AgentsRuntime model."""

    def test_create_runtime(self):
        """Test creating an agent runtime record."""
        runtime = AgentsRuntime(
            agent_id="agent-123",
            agent_name="TestAgent",
        )

        assert runtime.id == runtime.agent_run_id  # id is computed from agent_run_id
        assert runtime.agent_id == "agent-123"
        assert runtime.agent_name == "TestAgent"
        assert runtime.status == AgentsStatus.PENDING
        assert runtime.message is None
        assert runtime.tool_calls == {}
        assert runtime.streaming_text == ""
        assert runtime.error is None

    def test_runtime_id_computed_field(self):
        """Test that id is a computed field that returns agent_run_id."""
        runtime = AgentsRuntime(
            agent_id="custom-agent-id",
            agent_name="TestAgent",
        )

        # id should always equal agent_run_id
        assert runtime.id == runtime.agent_run_id
        assert runtime.agent_id == "custom-agent-id"

    def test_agent_run_id_is_timestamp(self):
        """Test that agent_run_id is a timestamp string for chronological ordering."""
        import time

        # Create first runtime
        runtime1 = AgentsRuntime(
            agent_id="agent-123",
            agent_name="TestAgent",
        )

        # Longer delay to ensure different timestamps
        time.sleep(0.1)

        # Create second runtime
        runtime2 = AgentsRuntime(
            agent_id="agent-123",
            agent_name="TestAgent",
        )

        # Both should have timestamp-based agent_run_id
        # Verify they are numeric strings (timestamps)
        assert runtime1.agent_run_id.replace(".", "").isdigit()
        assert runtime2.agent_run_id.replace(".", "").isdigit()

        # Verify they can be compared chronologically
        # runtime2 should have a larger timestamp than runtime1
        assert float(runtime2.agent_run_id) > float(runtime1.agent_run_id)

        # Verify id is computed from agent_run_id
        assert runtime1.id == runtime1.agent_run_id
        assert runtime2.id == runtime2.agent_run_id

    def test_runtime_status_transitions(self):
        """Test runtime status transitions."""
        runtime = AgentsRuntime(agent_id="agent-123")

        assert runtime.status == AgentsStatus.PENDING
        assert runtime.is_running is False
        assert runtime.is_completed is False

        runtime.status = AgentsStatus.EXECUTING
        assert runtime.is_running is True
        assert runtime.is_completed is False

        runtime.status = AgentsStatus.COMPLETED
        assert runtime.is_running is False
        assert runtime.is_completed is True

    def test_runtime_duration(self):
        """Test runtime duration calculation."""
        start = datetime(2024, 1, 1, 12, 0, 0)
        end = datetime(2024, 1, 1, 12, 0, 30)

        runtime = AgentsRuntime(
            agent_id="agent-123",
            started_at=start,
            completed_at=end,
        )

        assert runtime.duration == 30.0

    def test_runtime_duration_none_when_incomplete(self):
        """Test duration is None when execution is incomplete."""
        runtime = AgentsRuntime(
            agent_id="agent-123",
            started_at=datetime.now(),
        )

        assert runtime.duration is None

    def test_runtime_with_tool_calls(self):
        """Test runtime with tool calls."""
        runtime = AgentsRuntime(agent_id="agent-123")

        tool_call_1 = AgentsRuntimeToolCall(
            tool_use_id="tc-1",
            tool_name="calculator",
            tool_input={"expression": "2+2"},
            status="success",
        )

        tool_call_2 = AgentsRuntimeToolCall(
            tool_use_id="tc-2",
            tool_name="web_search",
            tool_input={"query": "test"},
            status="error",
            error="Network error",
        )

        runtime.tool_calls["tc-1"] = tool_call_1
        runtime.tool_calls["tc-2"] = tool_call_2

        assert runtime.tool_call_count == 2
        assert runtime.successful_tool_calls == 1
        assert runtime.failed_tool_calls == 1

    def test_runtime_with_streaming_text(self):
        """Test runtime with streaming text."""
        runtime = AgentsRuntime(agent_id="agent-123")

        runtime.streaming_text = "Hello"
        assert runtime.streaming_text == "Hello"

        runtime.streaming_text += " world"
        assert runtime.streaming_text == "Hello world"

    def test_runtime_with_error(self):
        """Test runtime with error."""
        runtime = AgentsRuntime(
            agent_id="agent-123",
            status=AgentsStatus.FAILED,
            error="Execution failed",
        )

        assert runtime.status == AgentsStatus.FAILED
        assert runtime.error == "Execution failed"
        assert runtime.is_completed is True

    def test_runtime_serialization(self):
        """Test runtime can be serialized to dict."""
        runtime = AgentsRuntime(
            agent_id="agent-123",
            agent_name="TestAgent",
            status=AgentsStatus.COMPLETED,
        )

        data = runtime.model_dump()

        assert data["agent_id"] == "agent-123"
        assert data["agent_name"] == "TestAgent"
        assert data["status"] == "completed"
        assert "id" in data
        assert data["id"] == runtime.agent_run_id  # id should equal agent_run_id
        assert "duration" in data
        assert "is_running" in data
        assert "is_completed" in data
        assert "tool_call_count" in data
        assert "successful_tool_calls" in data
        assert "failed_tool_calls" in data

    def test_tool_call_serialization(self):
        """Test tool call can be serialized to dict."""
        tool_call = AgentsRuntimeToolCall(
            tool_use_id="test-123",
            tool_name="calculator",
            tool_input={"expression": "2+2"},
            tool_result="4",
            status="success",
        )

        data = tool_call.model_dump()

        assert data["tool_use_id"] == "test-123"
        assert data["id"] == "test-123"  # id should equal tool_use_id
        assert data["tool_name"] == "calculator"
        assert data["tool_input"] == {"expression": "2+2"}
        assert data["tool_result"] == "4"
        assert data["status"] == "success"
        assert "duration" in data
        assert "is_completed" in data


class TestAgentsStatus:
    """Test AgentsStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert AgentsStatus.PENDING.value == "pending"
        assert AgentsStatus.EXECUTING.value == "executing"
        assert AgentsStatus.COMPLETED.value == "completed"
        assert AgentsStatus.FAILED.value == "failed"

    def test_status_comparison(self):
        """Test status comparison."""
        runtime = AgentsRuntime(agent_id="agent-123")

        runtime.status = AgentsStatus.PENDING
        assert runtime.status == AgentsStatus.PENDING

        runtime.status = AgentsStatus.EXECUTING
        assert runtime.status != AgentsStatus.PENDING
        assert runtime.status == AgentsStatus.EXECUTING

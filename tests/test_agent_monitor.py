"""
Unit tests for AgentsMonitor class.

Tests the agent execution monitoring functionality including:
- Initialization with and without callbacks
- Streaming event parsing and accumulation
- Tool event capture (toolUse and toolResult)
- Callback invocation with AgentsRuntime
- Error handling
- State access via tool_calls property
- Cleanup functionality
"""

from unittest.mock import Mock
from fivcadvisor.agents.types import AgentsMonitor, AgentsRuntime


class TestAgentsMonitorInitialization:
    """Test AgentsMonitor initialization."""

    def test_init_without_callbacks(self):
        """Test creating monitor without callbacks."""
        monitor = AgentsMonitor()

        assert monitor._on_event is None
        assert monitor._runtime is not None
        assert isinstance(monitor._runtime, AgentsRuntime)
        assert monitor._runtime.streaming_text == ""
        assert monitor.tool_calls == []

    def test_init_with_callback(self):
        """Test creating monitor with event callback."""
        on_event = Mock()

        monitor = AgentsMonitor(on_event=on_event)

        assert monitor._on_event is on_event
        assert monitor._runtime is not None

    def test_init_with_custom_runtime(self):
        """Test creating monitor with custom runtime."""
        custom_runtime = AgentsRuntime(agent_id="test-agent", streaming_text="initial")
        monitor = AgentsMonitor(runtime=custom_runtime)

        assert monitor._runtime is custom_runtime
        assert monitor._runtime.agent_id == "test-agent"
        assert monitor._runtime.streaming_text == "initial"


class TestAgentsMonitorStreaming:
    """Test streaming message tracking."""

    def test_handle_stream_event_single_chunk(self):
        """Test handling a single streaming chunk."""
        monitor = AgentsMonitor()

        # Create mock StreamEvent
        event = {"contentBlockDelta": {"delta": {"text": "Hello"}}}

        monitor(event=event)

        assert monitor._runtime.streaming_text == "Hello"

    def test_handle_stream_event_multiple_chunks(self):
        """Test accumulating multiple streaming chunks."""
        monitor = AgentsMonitor()

        chunks = ["Hello", " ", "world", "!"]
        for chunk in chunks:
            event = {"contentBlockDelta": {"delta": {"text": chunk}}}
            monitor(event=event)

        assert monitor._runtime.streaming_text == "Hello world!"

    def test_stream_callback_invoked_with_runtime(self):
        """Test that on_event callback is invoked with runtime after streaming."""
        on_event = Mock()
        monitor = AgentsMonitor(on_event=on_event)

        event = {"contentBlockDelta": {"delta": {"text": "test"}}}

        monitor(event=event)

        on_event.assert_called_once()
        # Verify the callback received the runtime
        call_args = on_event.call_args[0][0]
        assert isinstance(call_args, AgentsRuntime)
        assert call_args.streaming_text == "test"

    def test_stream_callback_multiple_invocations(self):
        """Test callback is invoked for each chunk with updated runtime."""
        captured_texts = []

        def on_event(runtime: AgentsRuntime):
            # Capture the streaming text at each invocation
            captured_texts.append(runtime.streaming_text)

        monitor = AgentsMonitor(on_event=on_event)

        chunks = ["a", "b", "c"]
        for chunk in chunks:
            event = {"contentBlockDelta": {"delta": {"text": chunk}}}
            monitor(event=event)

        # Verify callback was invoked 3 times with accumulated text
        assert len(captured_texts) == 3
        assert captured_texts[0] == "a"
        assert captured_texts[1] == "ab"
        assert captured_texts[2] == "abc"

    def test_content_block_start_clears_streaming_text(self):
        """Test that contentBlockStart clears streaming text."""
        monitor = AgentsMonitor()

        # Add some streaming text
        event1 = {"contentBlockDelta": {"delta": {"text": "old text"}}}
        monitor(event=event1)
        assert monitor._runtime.streaming_text == "old text"

        # contentBlockStart should clear it
        event2 = {"contentBlockStart": {}}
        monitor(event=event2)
        assert monitor._runtime.streaming_text == ""

    def test_malformed_stream_event(self):
        """Test handling malformed streaming events."""
        monitor = AgentsMonitor()

        # Missing delta
        event1 = {"contentBlockDelta": {}}
        monitor(event=event1)
        assert monitor._runtime.streaming_text == ""

        # Missing text
        event2 = {"contentBlockDelta": {"delta": {}}}
        monitor(event=event2)
        assert monitor._runtime.streaming_text == ""

        # Non-string text
        event3 = {"contentBlockDelta": {"delta": {"text": 123}}}
        monitor(event=event3)
        assert monitor._runtime.streaming_text == ""


class TestAgentsMonitorToolEvents:
    """Test tool call event tracking."""

    def test_handle_tool_use_event(self):
        """Test capturing tool use events."""
        monitor = AgentsMonitor()

        message = {
            "role": "assistant",
            "content": [
                {
                    "toolUse": {
                        "toolUseId": "123",
                        "name": "calculator",
                        "input": {"expression": "2+2"},
                    }
                }
            ],
        }

        monitor(message=message)

        tool_calls = monitor.tool_calls
        assert len(tool_calls) == 1
        assert tool_calls[0].tool_use_id == "123"
        assert tool_calls[0].tool_name == "calculator"
        assert tool_calls[0].tool_input == {"expression": "2+2"}
        assert tool_calls[0].status == "executing"

    def test_handle_tool_result_event(self):
        """Test capturing tool result events."""
        monitor = AgentsMonitor()

        # First add tool use
        message1 = {
            "role": "assistant",
            "content": [
                {"toolUse": {"toolUseId": "123", "name": "calculator", "input": {}}}
            ],
        }
        monitor(message=message1)

        # Then add tool result
        message2 = {
            "role": "user",
            "content": [
                {
                    "toolResult": {
                        "toolUseId": "123",
                        "content": [{"text": "4"}],
                        "status": "success",
                    }
                }
            ],
        }

        monitor(message=message2)

        tool_calls = monitor.tool_calls
        assert len(tool_calls) == 1
        assert tool_calls[0].tool_use_id == "123"
        assert tool_calls[0].status == "success"
        assert tool_calls[0].tool_result == [{"text": "4"}]

    def test_handle_tool_result_failure(self):
        """Test capturing failed tool result."""
        monitor = AgentsMonitor()

        # Add tool use
        message1 = {
            "role": "assistant",
            "content": [
                {"toolUse": {"toolUseId": "123", "name": "calculator", "input": {}}}
            ],
        }
        monitor(message=message1)

        # Add failed tool result
        message2 = {
            "role": "user",
            "content": [
                {
                    "toolResult": {
                        "toolUseId": "123",
                        "content": [{"text": "Error"}],
                        "status": "error",
                    }
                }
            ],
        }

        monitor(message=message2)

        tool_calls = monitor.tool_calls
        assert len(tool_calls) == 1
        assert tool_calls[0].status == "error"

    def test_tool_callback_invoked_with_runtime(self):
        """Test that on_event callback is invoked with runtime."""
        on_event = Mock()
        monitor = AgentsMonitor(on_event=on_event)

        message = {
            "role": "assistant",
            "content": [{"toolUse": {"toolUseId": "123", "name": "test", "input": {}}}],
        }

        monitor(message=message)

        on_event.assert_called_once()
        # Verify the callback received the runtime
        call_args = on_event.call_args[0][0]
        assert isinstance(call_args, AgentsRuntime)
        assert "123" in call_args.tool_calls

    def test_message_with_text_and_tool(self):
        """Test message containing both text and tool events."""
        monitor = AgentsMonitor()

        message = {
            "role": "assistant",
            "content": [
                {"text": "Let me calculate that"},
                {"toolUse": {"toolUseId": "123", "name": "calculator", "input": {}}},
            ],
        }

        monitor(message=message)

        # Tool events should be captured
        tool_calls = monitor.tool_calls
        assert len(tool_calls) == 1
        assert tool_calls[0].tool_name == "calculator"


class TestAgentsMonitorErrorHandling:
    """Test error handling in callbacks."""

    def test_stream_callback_exception_handled(self):
        """Test that event callback exceptions don't crash monitor during streaming."""

        def failing_callback(runtime):
            raise ValueError("Test error")

        monitor = AgentsMonitor(on_event=failing_callback)

        event = {"contentBlockDelta": {"delta": {"text": "test"}}}

        # Should not raise exception
        monitor(event=event)

        # Message should still be accumulated
        assert monitor._runtime.streaming_text == "test"

    def test_tool_callback_exception_handled(self):
        """Test that event callback exceptions don't crash monitor during tool events."""

        def failing_callback(runtime):
            raise ValueError("Test error")

        monitor = AgentsMonitor(on_event=failing_callback)

        message = {
            "role": "assistant",
            "content": [{"toolUse": {"toolUseId": "123", "name": "test", "input": {}}}],
        }

        # Should not raise exception
        monitor(message=message)

        # Event should still be captured
        assert len(monitor.tool_calls) == 1


class TestAgentsMonitorStateAccess:
    """Test state access via properties."""

    def test_tool_calls_property(self):
        """Test that tool_calls property returns list of tool calls."""
        monitor = AgentsMonitor()

        message = {
            "role": "assistant",
            "content": [{"toolUse": {"toolUseId": "123", "name": "test", "input": {}}}],
        }

        monitor(message=message)
        tool_calls = monitor.tool_calls

        assert len(tool_calls) == 1
        assert tool_calls[0].tool_use_id == "123"
        assert tool_calls[0].tool_name == "test"

    def test_runtime_access(self):
        """Test direct access to runtime for streaming text."""
        monitor = AgentsMonitor()

        event = {"contentBlockDelta": {"delta": {"text": "test message"}}}

        monitor(event=event)

        assert monitor._runtime.streaming_text == "test message"
        assert isinstance(monitor._runtime, AgentsRuntime)


class TestAgentsMonitorCleanup:
    """Test cleanup functionality."""

    def test_cleanup_clears_message(self):
        """Test that cleanup clears accumulated message."""
        monitor = AgentsMonitor()

        event = {"contentBlockDelta": {"delta": {"text": "test"}}}

        monitor(event=event)
        assert monitor._runtime.streaming_text == "test"

        monitor.cleanup()
        assert monitor._runtime.streaming_text == ""

    def test_cleanup_clears_tool_calls(self):
        """Test that cleanup clears tool events."""
        monitor = AgentsMonitor()

        message = {
            "role": "assistant",
            "content": [{"toolUse": {"toolUseId": "123", "name": "test", "input": {}}}],
        }

        monitor(message=message)
        assert len(monitor.tool_calls) == 1

        monitor.cleanup()
        assert len(monitor.tool_calls) == 0

    def test_cleanup_clears_callback(self):
        """Test that cleanup clears callback by default."""
        on_event = Mock()

        monitor = AgentsMonitor(on_event=on_event)
        monitor.cleanup()

        assert monitor._on_event is None

    def test_cleanup_with_new_callback(self):
        """Test that cleanup can set a new callback."""
        old_callback = Mock()
        new_callback = Mock()

        monitor = AgentsMonitor(on_event=old_callback)
        monitor.cleanup(on_event=new_callback)

        assert monitor._on_event is new_callback

    def test_cleanup_with_custom_runtime(self):
        """Test that cleanup can use a custom runtime."""
        monitor = AgentsMonitor()

        # Add some data
        event = {"contentBlockDelta": {"delta": {"text": "test"}}}
        monitor(event=event)

        # Cleanup with custom runtime
        custom_runtime = AgentsRuntime(agent_id="new-agent", streaming_text="new")
        monitor.cleanup(runtime=custom_runtime)

        assert monitor._runtime is custom_runtime
        assert monitor._runtime.agent_id == "new-agent"
        assert monitor._runtime.streaming_text == "new"

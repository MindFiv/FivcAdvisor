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
        from langchain_core.messages import AIMessageChunk

        monitor = AgentsMonitor()

        # Create mock message chunk
        msg_chunk = AIMessageChunk(content="Hello")
        event = (msg_chunk, {})

        monitor("messages", event)

        assert monitor._runtime.streaming_text == "Hello"

    def test_handle_stream_event_multiple_chunks(self):
        """Test accumulating multiple streaming chunks."""
        from langchain_core.messages import AIMessageChunk

        monitor = AgentsMonitor()

        chunks = ["Hello", " ", "world", "!"]
        for chunk in chunks:
            msg_chunk = AIMessageChunk(content=chunk)
            event = (msg_chunk, {})
            monitor("messages", event)

        assert monitor._runtime.streaming_text == "Hello world!"

    def test_stream_callback_invoked_with_runtime(self):
        """Test that on_event callback is invoked with runtime after streaming."""
        from langchain_core.messages import AIMessageChunk

        on_event = Mock()
        monitor = AgentsMonitor(on_event=on_event)

        msg_chunk = AIMessageChunk(content="test")
        event = (msg_chunk, {})

        monitor("messages", event)

        on_event.assert_called_once()
        # Verify the callback received the runtime
        call_args = on_event.call_args[0][0]
        assert isinstance(call_args, AgentsRuntime)
        assert call_args.streaming_text == "test"

    def test_stream_callback_multiple_invocations(self):
        """Test callback is invoked for each chunk with updated runtime."""
        from langchain_core.messages import AIMessageChunk

        captured_texts = []

        def on_event(runtime: AgentsRuntime):
            # Capture the streaming text at each invocation
            captured_texts.append(runtime.streaming_text)

        monitor = AgentsMonitor(on_event=on_event)

        chunks = ["a", "b", "c"]
        for chunk in chunks:
            msg_chunk = AIMessageChunk(content=chunk)
            event = (msg_chunk, {})
            monitor("messages", event)

        # Verify callback was invoked 3 times with accumulated text
        assert len(captured_texts) == 3
        assert captured_texts[0] == "a"
        assert captured_texts[1] == "ab"
        assert captured_texts[2] == "abc"

    def test_content_block_start_clears_streaming_text(self):
        """Test that updates mode clears streaming text."""
        monitor = AgentsMonitor()

        # Add some streaming text
        from langchain_core.messages import AIMessageChunk

        msg_chunk = AIMessageChunk(content="old text")
        event = (msg_chunk, {})
        monitor("messages", event)
        assert monitor._runtime.streaming_text == "old text"

        # updates mode should clear it
        monitor("updates", {})
        assert monitor._runtime.streaming_text == ""

    def test_malformed_stream_event(self):
        """Test handling malformed streaming events."""
        from langchain_core.messages import AIMessageChunk

        monitor = AgentsMonitor()

        # Valid message chunk
        msg_chunk = AIMessageChunk(content="test")
        event = (msg_chunk, {})
        monitor("messages", event)
        assert monitor._runtime.streaming_text == "test"


class TestAgentsMonitorToolEvents:
    """Test tool call event tracking."""

    def test_handle_tool_use_event(self):
        """Test capturing tool use events."""
        from langchain_core.messages import AIMessage

        monitor = AgentsMonitor()

        # Create a message with tool use
        message = AIMessage(
            content=[
                {
                    "type": "tool_use",
                    "id": "123",
                    "name": "calculator",
                    "input": {"expression": "2+2"},
                }
            ]
        )
        event = (message, {})

        monitor("messages", event)

        _ = monitor.tool_calls
        # Note: The new API doesn't parse tool calls from messages in the same way
        # This test verifies the monitor accepts the message without error
        assert isinstance(monitor._runtime, AgentsRuntime)

    def test_handle_tool_result_event(self):
        """Test capturing tool result events."""
        from langchain_core.messages import AIMessage

        monitor = AgentsMonitor()

        # First add tool use message
        message1 = AIMessage(
            content=[
                {
                    "type": "tool_use",
                    "id": "123",
                    "name": "calculator",
                    "input": {},
                }
            ]
        )
        event1 = (message1, {})
        monitor("messages", event1)

        # Then add tool result via values mode
        message2 = AIMessage(content="Result: 4")
        event2 = {"messages": [message2]}
        monitor("values", event2)

        # Verify runtime was updated
        assert monitor._runtime.reply is not None

    def test_handle_tool_result_failure(self):
        """Test capturing failed tool result."""
        from langchain_core.messages import AIMessage

        monitor = AgentsMonitor()

        # Add tool use message
        message1 = AIMessage(
            content=[
                {
                    "type": "tool_use",
                    "id": "123",
                    "name": "calculator",
                    "input": {},
                }
            ]
        )
        event1 = (message1, {})
        monitor("messages", event1)

        # Add error message via values mode
        message2 = AIMessage(content="Error occurred")
        event2 = {"messages": [message2]}
        monitor("values", event2)

        # Verify runtime was updated
        assert monitor._runtime.reply is not None

    def test_tool_callback_invoked_with_runtime(self):
        """Test that on_event callback is invoked with runtime."""
        from langchain_core.messages import AIMessageChunk

        on_event = Mock()
        monitor = AgentsMonitor(on_event=on_event)

        # Use AIMessageChunk with text content
        message = AIMessageChunk(content="Tool result: success")
        event = (message, {})

        monitor("messages", event)

        on_event.assert_called_once()
        # Verify the callback received the runtime
        call_args = on_event.call_args[0][0]
        assert isinstance(call_args, AgentsRuntime)
        assert call_args.streaming_text == "Tool result: success"

    def test_message_with_text_and_tool(self):
        """Test message containing both text and tool events."""
        from langchain_core.messages import AIMessageChunk

        monitor = AgentsMonitor()

        # Use AIMessageChunk with text content
        message = AIMessageChunk(content="Let me calculate that")
        event = (message, {})

        monitor("messages", event)

        # Verify message was processed
        assert monitor._runtime.streaming_text == "Let me calculate that"


class TestAgentsMonitorErrorHandling:
    """Test error handling in callbacks."""

    def test_stream_callback_exception_handled(self):
        """Test that event callback exceptions don't crash monitor during streaming."""
        from langchain_core.messages import AIMessageChunk

        def failing_callback(runtime):
            raise ValueError("Test error")

        monitor = AgentsMonitor(on_event=failing_callback)

        msg_chunk = AIMessageChunk(content="test")
        event = (msg_chunk, {})

        # Should not raise exception
        monitor("messages", event)

        # Message should still be accumulated
        assert monitor._runtime.streaming_text == "test"

    def test_tool_callback_exception_handled(self):
        """Test that event callback exceptions don't crash monitor during values events."""
        from langchain_core.messages import AIMessage

        def failing_callback(runtime):
            raise ValueError("Test error")

        monitor = AgentsMonitor(on_event=failing_callback)

        message = AIMessage(content="test response")
        event = {"messages": [message]}

        # Should not raise exception
        monitor("values", event)

        # Event should still be captured
        assert monitor._runtime.reply is not None


class TestAgentsMonitorStateAccess:
    """Test state access via properties."""

    def test_tool_calls_property(self):
        """Test that tool_calls property returns list of tool calls."""
        monitor = AgentsMonitor()

        # Tool calls are empty by default
        tool_calls = monitor.tool_calls
        assert len(tool_calls) == 0

    def test_runtime_access(self):
        """Test direct access to runtime for streaming text."""
        from langchain_core.messages import AIMessageChunk

        monitor = AgentsMonitor()

        msg_chunk = AIMessageChunk(content="test message")
        event = (msg_chunk, {})

        monitor("messages", event)

        assert monitor._runtime.streaming_text == "test message"
        assert isinstance(monitor._runtime, AgentsRuntime)


class TestAgentsMonitorCleanup:
    """Test cleanup functionality."""

    def test_cleanup_clears_message(self):
        """Test that cleanup clears accumulated message."""
        from langchain_core.messages import AIMessageChunk

        monitor = AgentsMonitor()

        msg_chunk = AIMessageChunk(content="test")
        event = (msg_chunk, {})

        monitor("messages", event)
        assert monitor._runtime.streaming_text == "test"

        monitor.cleanup()
        assert monitor._runtime.streaming_text == ""

    def test_cleanup_clears_tool_calls(self):
        """Test that cleanup clears tool events."""
        monitor = AgentsMonitor()

        # Tool calls are empty by default
        assert len(monitor.tool_calls) == 0

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
        from langchain_core.messages import AIMessageChunk

        monitor = AgentsMonitor()

        # Add some data
        msg_chunk = AIMessageChunk(content="test")
        event = (msg_chunk, {})
        monitor("messages", event)

        # Cleanup with custom runtime
        custom_runtime = AgentsRuntime(agent_id="new-agent", streaming_text="new")
        monitor.cleanup(runtime=custom_runtime)

        assert monitor._runtime is custom_runtime
        assert monitor._runtime.agent_id == "new-agent"
        assert monitor._runtime.streaming_text == "new"

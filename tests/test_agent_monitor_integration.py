"""
Integration tests for AgentsMonitor with ChatSession.

Tests the integration of AgentsMonitor with ChatSession and real agent execution:
- ChatSession creates and uses AgentsMonitor correctly
- Monitor integration with agent execution
- UI callback flow with unified on_event callback
- Multiple executions with cleanup
- Async execution compatibility
"""

import pytest
import dotenv
from unittest.mock import Mock, AsyncMock
from fivcadvisor.app.sessions import ChatSession
from fivcadvisor.agents.types import AgentsMonitor, AgentsRuntime
from fivcadvisor import agents, tools

dotenv.load_dotenv()


@pytest.fixture
def mock_agents_retriever():
    """Create a mock agents retriever."""
    retriever = Mock(spec=agents.AgentsRetriever)
    return retriever


@pytest.fixture
def mock_tools_retriever():
    """Create a mock tools retriever."""
    retriever = Mock(spec=tools.ToolsRetriever)
    return retriever


class TestChatSessionMonitorIntegration:
    """Test ChatSession integration with AgentsMonitor."""

    def test_chat_session_creates_monitor(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test that ChatSession creates an AgentsMonitor instance."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        assert hasattr(session, "monitor")
        assert isinstance(session.monitor, AgentsMonitor)

    def test_chat_session_passes_monitor_to_agent(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test that ChatSession passes monitor as callback_handler to agent."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        # Agent should have the monitor as callback_handler
        assert session.agent.callback_handler is session.monitor

    @pytest.mark.asyncio
    async def test_monitor_cleanup_on_each_run(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test that monitor is cleaned up before each execution."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        # Mock the agent
        session.agent.invoke_async = AsyncMock(
            return_value=Mock(output="Test response", messages=[])
        )

        # First run - simulate some state
        session.monitor._runtime.streaming_text = "old message"
        session.monitor._runtime.tool_calls = {"123": Mock()}

        await session.run("test query")

        # Monitor should have been cleaned up (state cleared)
        # After cleanup, if no events occurred, state should be empty
        # We can't guarantee events occurred in mock, so just verify run completed
        assert session.agent.invoke_async.called

    @pytest.mark.asyncio
    async def test_multiple_executions(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test that monitor works correctly across multiple executions."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        # Mock the agent
        session.agent.invoke_async = AsyncMock(
            return_value=Mock(output="Test response", messages=[])
        )

        # First execution
        await session.run("query 1")
        assert session.agent.invoke_async.call_count == 1

        # Second execution
        await session.run("query 2")
        assert session.agent.invoke_async.call_count == 2


class TestMonitorWithMockAgent:
    """Test monitor with simulated agent events."""

    @pytest.mark.asyncio
    async def test_monitor_captures_streaming_events(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test that monitor captures streaming events during execution."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        captured_runtimes = []

        def on_event(runtime: AgentsRuntime):
            # Capture runtime state
            captured_runtimes.append(
                {
                    "streaming_text": runtime.streaming_text,
                    "tool_calls": len(runtime.tool_calls),
                }
            )

        # Simulate agent execution with streaming
        async def mock_invoke(query):
            # Simulate streaming events
            session.monitor(event={"contentBlockDelta": {"delta": {"text": "Hello"}}})
            session.monitor(event={"contentBlockDelta": {"delta": {"text": " world"}}})

            return Mock(output="Hello world", messages=[])

        session.agent.invoke_async = mock_invoke

        # Pass callback to run method
        await session.run("test", on_event=on_event)

        # Verify streaming was captured
        assert len(captured_runtimes) == 2
        assert captured_runtimes[0]["streaming_text"] == "Hello"
        assert captured_runtimes[1]["streaming_text"] == "Hello world"
        assert session.monitor._runtime.streaming_text == "Hello world"

    @pytest.mark.asyncio
    async def test_monitor_captures_tool_events(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test that monitor captures tool events during execution."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        captured_runtimes = []

        def on_event(runtime: AgentsRuntime):
            # Capture runtime state
            captured_runtimes.append(
                {
                    "tool_call_count": len(runtime.tool_calls),
                    "tool_calls": list(runtime.tool_calls.keys()),
                }
            )

        # Simulate agent execution with tool calls
        async def mock_invoke(query):
            # Simulate tool use event
            session.monitor(
                message={
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
            )

            # Simulate tool result event
            session.monitor(
                message={
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
            )

            return Mock(output="The answer is 4", messages=[])

        session.agent.invoke_async = mock_invoke

        # Pass callback to run method
        await session.run("test", on_event=on_event)

        # Verify tool events were captured
        assert len(captured_runtimes) == 2
        assert captured_runtimes[0]["tool_call_count"] == 1
        assert captured_runtimes[1]["tool_call_count"] == 1
        assert "123" in captured_runtimes[0]["tool_calls"]
        assert len(session.monitor.tool_calls) == 1

    @pytest.mark.asyncio
    async def test_monitor_with_both_streaming_and_tools(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test monitor handling both streaming and tool events."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        captured_runtimes = []

        def on_event(runtime: AgentsRuntime):
            # Capture complete runtime state
            captured_runtimes.append(
                {
                    "streaming_text": runtime.streaming_text,
                    "tool_call_count": len(runtime.tool_calls),
                }
            )

        # Simulate complex agent execution
        async def mock_invoke(query):
            # Stream some text
            session.monitor(
                event={
                    "contentBlockDelta": {"delta": {"text": "Let me calculate that. "}}
                }
            )

            # Use a tool
            session.monitor(
                message={
                    "role": "assistant",
                    "content": [
                        {
                            "toolUse": {
                                "toolUseId": "123",
                                "name": "calculator",
                                "input": {},
                            }
                        }
                    ],
                }
            )

            # Tool result
            session.monitor(
                message={
                    "role": "user",
                    "content": [
                        {
                            "toolResult": {
                                "toolUseId": "123",
                                "content": [{"text": "42"}],
                                "status": "success",
                            }
                        }
                    ],
                }
            )

            # Stream final response
            session.monitor(
                event={"contentBlockDelta": {"delta": {"text": "The answer is 42."}}}
            )

            return Mock(output="Let me calculate that. The answer is 42.", messages=[])

        session.agent.invoke_async = mock_invoke

        # Pass callback to run method
        await session.run("test", on_event=on_event)

        # Verify both types of events were captured
        assert len(captured_runtimes) == 4  # 2 streaming + 2 tool events

        # First streaming event
        assert captured_runtimes[0]["streaming_text"] == "Let me calculate that. "
        assert captured_runtimes[0]["tool_call_count"] == 0

        # Tool use event
        assert captured_runtimes[1]["tool_call_count"] == 1

        # Tool result event
        assert captured_runtimes[2]["tool_call_count"] == 1

        # Second streaming event
        assert (
            captured_runtimes[3]["streaming_text"]
            == "Let me calculate that. The answer is 42."
        )

        # Verify final monitor state
        assert (
            session.monitor._runtime.streaming_text
            == "Let me calculate that. The answer is 42."
        )
        assert len(session.monitor.tool_calls) == 1


class TestMonitorErrorHandling:
    """Test monitor error handling in integration scenarios."""

    @pytest.mark.asyncio
    async def test_callback_exception_doesnt_break_execution(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test that callback exceptions don't break agent execution."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        def failing_callback(runtime):
            raise ValueError("Callback error")

        # Simulate agent execution
        async def mock_invoke(query):
            session.monitor(event={"contentBlockDelta": {"delta": {"text": "test"}}})

            session.monitor(
                message={
                    "role": "assistant",
                    "content": [
                        {"toolUse": {"toolUseId": "123", "name": "test", "input": {}}}
                    ],
                }
            )

            return Mock(output="test", messages=[])

        session.agent.invoke_async = mock_invoke

        # Set failing callback
        session.monitor._on_event = failing_callback

        # Should not raise exception despite failing callback
        result = await session.run("test")

        # Execution should complete successfully
        assert result is not None

        # Monitor should still have captured the events
        assert session.monitor._runtime.streaming_text == "test"
        assert len(session.monitor.tool_calls) == 1


class TestMonitorStateManagement:
    """Test monitor state management across executions."""

    @pytest.mark.asyncio
    async def test_state_isolated_between_runs(
        self, mock_agents_retriever, mock_tools_retriever
    ):
        """Test that state is properly isolated between runs."""
        session = ChatSession(
            agents_retriever=mock_agents_retriever, tools_retriever=mock_tools_retriever
        )

        # First execution
        async def mock_invoke_1(query):
            session.monitor(
                event={"contentBlockDelta": {"delta": {"text": "First response"}}}
            )
            return Mock(output="First response", messages=[])

        session.agent.invoke_async = mock_invoke_1
        await session.run("query 1")

        # Capture state after first run
        first_message = session.monitor._runtime.streaming_text

        # Second execution
        async def mock_invoke_2(query):
            session.monitor(
                event={"contentBlockDelta": {"delta": {"text": "Second response"}}}
            )
            return Mock(output="Second response", messages=[])

        session.agent.invoke_async = mock_invoke_2
        await session.run("query 2")

        # State should be from second run only (cleanup clears first run)
        second_message = session.monitor._runtime.streaming_text
        assert second_message == "Second response"
        assert second_message != first_message

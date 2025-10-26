"""
Integration tests for AgentsMonitor with Chat.

Tests the integration of AgentsMonitor with Chat and real agent execution:
- Chat uses AgentsMonitorManager correctly
- Monitor integration with agent execution
- UI callback flow with unified on_event callback
- Multiple executions with cleanup
- Async execution compatibility
"""

import pytest
import dotenv
from unittest.mock import Mock, AsyncMock, patch
from fivcadvisor.app.utils.chats import Chat
from fivcadvisor.agents.types import AgentsMonitor, AgentsRuntime
from fivcadvisor import tools

dotenv.load_dotenv()


@pytest.fixture
def mock_tools_retriever():
    """Create a mock tools retriever."""
    retriever = Mock(spec=tools.ToolsRetriever)
    retriever.retrieve.return_value = []
    # Mock to_tool() to return a valid tool spec
    mock_tool = Mock()
    mock_tool.name = "mock_tool"
    retriever.to_tool.return_value = mock_tool
    return retriever


class TestChatMonitorIntegration:
    """Test Chat integration with AgentsMonitor."""

    def test_chat_creates_monitor_manager(self, mock_tools_retriever):
        """Test that Chat creates an AgentsMonitorManager instance."""
        manager = Chat(tools_retriever=mock_tools_retriever)

        assert hasattr(manager, "monitor_manager")
        from fivcadvisor.agents.types import AgentsMonitorManager

        assert isinstance(manager.monitor_manager, AgentsMonitorManager)

    @pytest.mark.asyncio
    async def test_multiple_executions(self, mock_tools_retriever):
        """Test that monitor works correctly across multiple executions."""
        from fivcadvisor.agents.types.repositories import AgentsRuntimeRepository

        mock_repo = Mock(spec=AgentsRuntimeRepository)

        manager = Chat(
            agent_runtime_repo=mock_repo, tools_retriever=mock_tools_retriever
        )

        # Mock the agent creation and execution
        mock_agent = Mock()
        mock_agent.agent_id = "test-agent-id"
        mock_agent.name = "TestAgent"
        mock_agent.system_prompt = "Test prompt"
        mock_agent.run_async = AsyncMock(
            return_value=Mock(output="Test response", message={})
        )

        with patch.object(
            manager.monitor_manager, "create_agent_runtime", return_value=mock_agent
        ):
            # Mock create_briefing_task to avoid actual agent creation
            with patch(
                "fivcadvisor.app.utils.chats.tasks.create_briefing_task"
            ) as mock_briefing_task:
                # Mock the task to return a mock with run_async method
                mock_task = Mock()
                mock_task.run_async = AsyncMock(return_value="Agent description")
                mock_briefing_task.return_value = mock_task

                # First execution - should call briefing task to create agent metadata
                await manager.ask("query 1")
                assert mock_briefing_task.call_count == 1

                # Second execution - should NOT call briefing task (metadata already exists)
                await manager.ask("query 2")
                assert mock_briefing_task.call_count == 1  # Still 1, not 2


class TestMonitorWithMockAgent:
    """Test monitor with simulated agent events."""

    @pytest.mark.asyncio
    async def test_monitor_captures_streaming_events(self, mock_tools_retriever):
        """Test that monitor captures streaming events during execution."""
        from fivcadvisor.agents.types.repositories import AgentsRuntimeRepository

        mock_repo = Mock(spec=AgentsRuntimeRepository)

        manager = Chat(
            agent_runtime_repo=mock_repo, tools_retriever=mock_tools_retriever
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

        # Create a mock monitor that simulates streaming
        mock_monitor = Mock(spec=AgentsMonitor)
        mock_monitor.id = "test-monitor"
        mock_monitor.is_completed = False
        mock_monitor.status = "executing"

        # Mock agent that triggers events
        mock_agent = Mock()
        mock_agent.agent_id = "test-agent-id"
        mock_agent.name = "TestAgent"
        mock_agent.system_prompt = "Test prompt"

        async def mock_invoke(query):
            # Simulate streaming events through callback
            runtime = AgentsRuntime(agent_id="test-agent-id", streaming_text="Hello")
            on_event(runtime)
            runtime.streaming_text = "Hello world"
            on_event(runtime)
            return Mock(output="Hello world", message={})

        mock_agent.run_async = mock_invoke

        with patch.object(
            manager.monitor_manager, "create_agent_runtime", return_value=mock_agent
        ):
            # Mock create_briefing_task to avoid actual agent creation
            with patch(
                "fivcadvisor.app.utils.chats.tasks.create_briefing_task"
            ) as mock_briefing_task:
                # Mock the task to return a mock with run_async method
                mock_task = Mock()
                mock_task.run_async = AsyncMock(return_value="Agent description")
                mock_briefing_task.return_value = mock_task

                # Pass callback to ask method
                await manager.ask("test", on_event=on_event)

        # Verify streaming was captured
        assert len(captured_runtimes) == 2
        assert captured_runtimes[0]["streaming_text"] == "Hello"
        assert captured_runtimes[1]["streaming_text"] == "Hello world"

    @pytest.mark.asyncio
    async def test_monitor_captures_tool_events(self, mock_tools_retriever):
        """Test that monitor captures tool events during execution."""
        from fivcadvisor.agents.types.repositories import AgentsRuntimeRepository

        mock_repo = Mock(spec=AgentsRuntimeRepository)

        manager = Chat(
            agent_runtime_repo=mock_repo, tools_retriever=mock_tools_retriever
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

        # Mock agent that triggers tool events
        mock_agent = Mock()
        mock_agent.agent_id = "test-agent-id"
        mock_agent.name = "TestAgent"
        mock_agent.system_prompt = "Test prompt"

        async def mock_invoke(query):
            # Simulate tool use and result events through callback
            from fivcadvisor.agents.types import AgentsRuntimeToolCall

            runtime = AgentsRuntime(agent_id="test-agent-id")
            runtime.tool_calls["123"] = AgentsRuntimeToolCall(
                tool_use_id="123", tool_name="calculator", status="pending"
            )
            on_event(runtime)

            runtime.tool_calls["123"].status = "success"
            on_event(runtime)

            return Mock(output="The answer is 4", message={})

        mock_agent.run_async = mock_invoke

        with patch.object(
            manager.monitor_manager, "create_agent_runtime", return_value=mock_agent
        ):
            # Mock create_briefing_task to avoid actual agent creation
            with patch(
                "fivcadvisor.app.utils.chats.tasks.create_briefing_task"
            ) as mock_briefing_task:
                # Mock the task to return a mock with run_async method
                mock_task = Mock()
                mock_task.run_async = AsyncMock(return_value="Agent description")
                mock_briefing_task.return_value = mock_task

                # Pass callback to ask method
                await manager.ask("test", on_event=on_event)

        # Verify tool events were captured
        assert len(captured_runtimes) == 2
        assert captured_runtimes[0]["tool_call_count"] == 1
        assert captured_runtimes[1]["tool_call_count"] == 1
        assert "123" in captured_runtimes[0]["tool_calls"]

    @pytest.mark.asyncio
    async def test_monitor_with_both_streaming_and_tools(self, mock_tools_retriever):
        """Test monitor handling both streaming and tool events."""
        from fivcadvisor.agents.types.repositories import AgentsRuntimeRepository

        mock_repo = Mock(spec=AgentsRuntimeRepository)

        manager = Chat(
            agent_runtime_repo=mock_repo, tools_retriever=mock_tools_retriever
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

        # Mock agent that triggers both streaming and tool events
        mock_agent = Mock()
        mock_agent.agent_id = "test-agent-id"
        mock_agent.name = "TestAgent"
        mock_agent.system_prompt = "Test prompt"

        async def mock_invoke(query):
            from fivcadvisor.agents.types import AgentsRuntimeToolCall

            runtime = AgentsRuntime(agent_id="test-agent-id")

            # Stream some text
            runtime.streaming_text = "Let me calculate that. "
            on_event(runtime)

            # Use a tool
            runtime.tool_calls["123"] = AgentsRuntimeToolCall(
                tool_use_id="123", tool_name="calculator", status="pending"
            )
            on_event(runtime)

            # Tool result
            runtime.tool_calls["123"].status = "success"
            on_event(runtime)

            # Stream final response
            runtime.streaming_text = "Let me calculate that. The answer is 42."
            on_event(runtime)

            return Mock(output="Let me calculate that. The answer is 42.", message={})

        mock_agent.run_async = mock_invoke

        with patch.object(
            manager.monitor_manager, "create_agent_runtime", return_value=mock_agent
        ):
            # Mock create_briefing_task to avoid actual agent creation
            with patch(
                "fivcadvisor.app.utils.chats.tasks.create_briefing_task"
            ) as mock_briefing_task:
                # Mock the task to return a mock with run_async method
                mock_task = Mock()
                mock_task.run_async = AsyncMock(return_value="Agent description")
                mock_briefing_task.return_value = mock_task

                # Pass callback to ask method
                await manager.ask("test", on_event=on_event)

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


class TestMonitorErrorHandling:
    """Test monitor error handling in integration scenarios."""

    @pytest.mark.asyncio
    async def test_callback_exception_doesnt_break_execution(
        self, mock_tools_retriever
    ):
        """Test that callback exceptions don't break agent execution."""
        from fivcadvisor.agents.types.repositories import AgentsRuntimeRepository

        mock_repo = Mock(spec=AgentsRuntimeRepository)

        manager = Chat(
            agent_runtime_repo=mock_repo, tools_retriever=mock_tools_retriever
        )

        def failing_callback(runtime):
            raise ValueError("Callback error")

        # Mock agent
        mock_agent = Mock()
        mock_agent.agent_id = "test-agent-id"
        mock_agent.name = "TestAgent"
        mock_agent.system_prompt = "Test prompt"

        async def mock_invoke(query):
            # Even with failing callback, execution should continue
            return Mock(output="test", message={})

        mock_agent.run_async = mock_invoke

        with patch.object(
            manager.monitor_manager, "create_agent_runtime", return_value=mock_agent
        ):
            # Mock create_briefing_task to avoid actual agent creation
            with patch(
                "fivcadvisor.app.utils.chats.tasks.create_briefing_task"
            ) as mock_briefing_task:
                # Mock the task to return a mock with run_async method
                mock_task = Mock()
                mock_task.run_async = AsyncMock(return_value="Agent description")
                mock_briefing_task.return_value = mock_task

                # Should not raise exception despite failing callback
                result = await manager.ask("test", on_event=failing_callback)

                # Execution should complete successfully
                assert result is not None


class TestMonitorStateManagement:
    """Test monitor state management across executions."""

    @pytest.mark.asyncio
    async def test_state_isolated_between_runs(self, mock_tools_retriever):
        """Test that state is properly isolated between runs."""
        from fivcadvisor.agents.types.repositories import AgentsRuntimeRepository

        mock_repo = Mock(spec=AgentsRuntimeRepository)

        manager = Chat(
            agent_runtime_repo=mock_repo, tools_retriever=mock_tools_retriever
        )

        captured_first = []
        captured_second = []

        def on_event_first(runtime: AgentsRuntime):
            captured_first.append(runtime.streaming_text)

        def on_event_second(runtime: AgentsRuntime):
            captured_second.append(runtime.streaming_text)

        # Mock agents for each execution
        mock_agent_1 = Mock()
        mock_agent_1.agent_id = "test-agent-id"
        mock_agent_1.name = "TestAgent"
        mock_agent_1.system_prompt = "Test prompt"

        mock_agent_2 = Mock()
        mock_agent_2.agent_id = "test-agent-id"
        mock_agent_2.name = "TestAgent"
        mock_agent_2.system_prompt = "Test prompt"

        async def mock_invoke_1(query):
            runtime = AgentsRuntime(agent_id="test-agent-id")
            runtime.streaming_text = "First response"
            on_event_first(runtime)
            return Mock(output="First response", message={})

        async def mock_invoke_2(query):
            runtime = AgentsRuntime(agent_id="test-agent-id")
            runtime.streaming_text = "Second response"
            on_event_second(runtime)
            return Mock(output="Second response", message={})

        mock_agent_1.run_async = mock_invoke_1
        mock_agent_2.run_async = mock_invoke_2

        # First execution
        with patch.object(
            manager.monitor_manager, "create_agent_runtime", return_value=mock_agent_1
        ):
            # Mock create_briefing_task to avoid actual agent creation
            with patch(
                "fivcadvisor.app.utils.chats.tasks.create_briefing_task"
            ) as mock_briefing_task:
                # Mock the task to return a mock with run_async method
                mock_task = Mock()
                mock_task.run_async = AsyncMock(return_value="Agent description")
                mock_briefing_task.return_value = mock_task
                await manager.ask("query 1", on_event=on_event_first)

        # Second execution
        with patch.object(
            manager.monitor_manager, "create_agent_runtime", return_value=mock_agent_2
        ):
            # Mock create_briefing_task to avoid actual agent creation
            with patch(
                "fivcadvisor.app.utils.chats.tasks.create_briefing_task"
            ) as mock_briefing_task:
                # Mock the task to return a mock with run_async method
                mock_task = Mock()
                mock_task.run_async = AsyncMock(return_value="Agent description")
                mock_briefing_task.return_value = mock_task
                await manager.ask("query 2", on_event=on_event_second)

        # State should be isolated between runs
        assert captured_first[0] == "First response"
        assert captured_second[0] == "Second response"
        assert captured_first[0] != captured_second[0]

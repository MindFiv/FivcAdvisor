#!/usr/bin/env python3
"""
Tests for AgentsMonitorManager functionality.
"""

import os
import tempfile
from unittest.mock import Mock, MagicMock

from fivcadvisor.agents.types import (
    AgentsMonitorManager,
    AgentsMonitor,
    # AgentsRuntime,
    AgentsRuntimeToolCall,
    AgentsStatus,
)
from fivcadvisor.agents.types.repositories.files import FileAgentsRuntimeRepository
from fivcadvisor.utils import OutputDir


class TestAgentsMonitorManager:
    """Tests for AgentsMonitorManager class"""

    def test_initialization(self):
        """Test AgentsMonitorManager initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)
            manager = AgentsMonitorManager(runtime_repo=repo)

            # Manager should have a repository
            assert manager._repo is not None
            assert isinstance(manager._repo, FileAgentsRuntimeRepository)

    def test_create_agent_runtime(self):
        """Test creating an agent runtime with monitoring"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)
            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            # Create mock tools with name attribute
            mock_tool1 = Mock()
            mock_tool1.name = "tool1"
            mock_tool2 = Mock()
            mock_tool2.name = "tool2"
            mock_tools_retriever.retrieve.return_value = [mock_tool1, mock_tool2]

            mock_agent = MagicMock()
            mock_agent_creator = Mock(return_value=mock_agent)
            mock_agent_creator.name = "TestAgent"

            agent = manager.create_agent_runtime(
                query="Test query",
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )

            # Verify agent was created
            assert agent is not None
            assert agent == mock_agent

            # Verify tools were retrieved with expand=True
            mock_tools_retriever.retrieve.assert_called_once_with(
                "Test query", expand=True
            )

            # Verify agent creator was called with correct parameters
            mock_agent_creator.assert_called_once()
            call_kwargs = mock_agent_creator.call_args[1]
            assert "agent_id" in call_kwargs
            assert "callback_handler" in call_kwargs
            assert "tools" in call_kwargs
            # Verify tools were passed (check names)
            tools = call_kwargs["tools"]
            assert len(tools) == 2
            assert tools[0].name == "tool1"
            assert tools[1].name == "tool2"
            assert isinstance(call_kwargs["callback_handler"], AgentsMonitor)

            # Verify agent runtime was persisted
            agent_id = call_kwargs["agent_id"]
            agent_monitor = call_kwargs["callback_handler"]
            agent_run_id = agent_monitor._runtime.agent_run_id
            agent_runtime = repo.get_agent_runtime(agent_id, agent_run_id)
            assert agent_runtime is not None
            assert agent_runtime.query == "Test query"

    def test_create_agent_runtime_with_callback(self):
        """Test creating an agent runtime with event callback"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)
            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            callback = Mock()
            _ = manager.create_agent_runtime(
                query="Test query",
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
                on_event=callback,
            )

            # Verify callback was passed to monitor
            call_kwargs = mock_agent_creator.call_args[1]
            monitor = call_kwargs["callback_handler"]
            assert monitor._on_event == callback

    def test_create_agent_runtime_auto_generates_id(self):
        """Test that agent ID is auto-generated"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)
            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            _ = manager.create_agent_runtime(
                query="Test query",
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )

            # Verify agent ID was auto-generated
            call_kwargs = mock_agent_creator.call_args[1]
            agent_id = call_kwargs["agent_id"]
            assert agent_id is not None
            assert len(agent_id) > 0

            # Verify agent was persisted
            agent_monitor = call_kwargs["callback_handler"]
            agent_run_id = agent_monitor._runtime.agent_run_id
            agent_runtime = repo.get_agent_runtime(agent_id, agent_run_id)
            assert agent_runtime is not None

    def test_list_agent_runtimes(self):
        """Test listing agent runtimes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)
            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            # Create some agent runtimes through the manager with same agent_id
            agent_id = "test-agent-123"
            _ = manager.create_agent_runtime(
                query="Query 1",
                agent_id=agent_id,
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            _ = manager.create_agent_runtime(
                query="Query 2",
                agent_id=agent_id,
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )

            monitors = manager.list_agent_runtimes(agent_id)
            assert len(monitors) == 2

            # Verify both agent runtimes are in the list
            assert all(isinstance(m, AgentsMonitor) for m in monitors)

    def test_list_agent_runtimes_empty(self):
        """Test listing agent runtimes when repository is empty"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            manager = AgentsMonitorManager(runtime_repo=repo)

            agents = manager.list_agent_runtimes("nonexistent-agent")
            assert agents == []

    def test_list_agent_runtimes_with_status_filter(self):
        """Test listing agent runtimes filtered by status"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            # Use same agent_id for all runtimes
            agent_id = "test-agent-123"

            # Create agent runtimes and manually set their statuses
            _ = manager.create_agent_runtime(
                query="Query 1",
                agent_id=agent_id,
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            agent1_monitor = mock_agent_creator.call_args_list[0][1]["callback_handler"]
            agent1_run_id = agent1_monitor._runtime.agent_run_id
            runtime1 = repo.get_agent_runtime(agent_id, agent1_run_id)
            runtime1.status = AgentsStatus.PENDING
            repo.update_agent_runtime(agent_id, runtime1)

            _ = manager.create_agent_runtime(
                query="Query 2",
                agent_id=agent_id,
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            agent2_monitor = mock_agent_creator.call_args_list[1][1]["callback_handler"]
            agent2_run_id = agent2_monitor._runtime.agent_run_id
            runtime2 = repo.get_agent_runtime(agent_id, agent2_run_id)
            runtime2.status = AgentsStatus.EXECUTING
            repo.update_agent_runtime(agent_id, runtime2)

            _ = manager.create_agent_runtime(
                query="Query 3",
                agent_id=agent_id,
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            agent3_monitor = mock_agent_creator.call_args_list[2][1]["callback_handler"]
            agent3_run_id = agent3_monitor._runtime.agent_run_id
            runtime3 = repo.get_agent_runtime(agent_id, agent3_run_id)
            runtime3.status = AgentsStatus.COMPLETED
            repo.update_agent_runtime(agent_id, runtime3)

            # Filter by EXECUTING status
            executing_agents = manager.list_agent_runtimes(
                agent_id, status=[AgentsStatus.EXECUTING]
            )
            assert len(executing_agents) == 1
            assert executing_agents[0]._runtime.agent_run_id == agent2_run_id

            # Filter by multiple statuses
            pending_or_completed = manager.list_agent_runtimes(
                agent_id, status=[AgentsStatus.PENDING, AgentsStatus.COMPLETED]
            )
            assert len(pending_or_completed) == 2
            run_ids = {agent._runtime.agent_run_id for agent in pending_or_completed}
            assert agent1_run_id in run_ids
            assert agent3_run_id in run_ids

    def test_get_agent_runtime(self):
        """Test getting a specific agent runtime monitor"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            _ = manager.create_agent_runtime(
                query="Test query",
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            agent_id = mock_agent_creator.call_args[1]["agent_id"]
            agent_monitor = mock_agent_creator.call_args[1]["callback_handler"]
            agent_run_id = agent_monitor._runtime.agent_run_id

            result = manager.get_agent_runtime(agent_id, agent_run_id)
            assert result is not None
            assert isinstance(result, AgentsMonitor)
            assert result._runtime.agent_id == agent_id

    def test_get_agent_runtime_nonexistent(self):
        """Test getting a nonexistent agent runtime"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            manager = AgentsMonitorManager(runtime_repo=repo)

            result = manager.get_agent_runtime("nonexistent", "nonexistent-run")
            assert result is None

    def test_get_agent_runtime_with_callback(self):
        """Test getting an agent runtime monitor with event callback"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            _ = manager.create_agent_runtime(
                query="Test query",
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            agent_id = mock_agent_creator.call_args[1]["agent_id"]
            agent_monitor = mock_agent_creator.call_args[1]["callback_handler"]
            agent_run_id = agent_monitor._runtime.agent_run_id

            callback = Mock()
            result = manager.get_agent_runtime(
                agent_id, agent_run_id, on_event=callback
            )
            assert result is not None
            assert result._on_event == callback

    def test_delete_agent_runtime(self):
        """Test deleting an agent runtime"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            agent_id = "test-agent-123"
            _ = manager.create_agent_runtime(
                query="Test query",
                agent_id=agent_id,
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            agent_monitor = mock_agent_creator.call_args[1]["callback_handler"]
            agent_run_id = agent_monitor._runtime.agent_run_id

            assert len(manager.list_agent_runtimes(agent_id)) == 1

            manager.delete_agent_runtime(agent_id, agent_run_id)

            assert len(manager.list_agent_runtimes(agent_id)) == 0

    def test_delete_agent_runtime_nonexistent(self):
        """Test deleting a nonexistent agent runtime (should not raise error)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            manager = AgentsMonitorManager(runtime_repo=repo)

            # Should not raise error
            manager.delete_agent_runtime("nonexistent", "nonexistent-run")

    def test_save_and_load(self):
        """Test saving and loading agent runtimes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create manager and add data
            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            agent_id = "test-agent-123"
            _ = manager.create_agent_runtime(
                query="Test query",
                agent_id=agent_id,
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            agent_monitor = mock_agent_creator.call_args[1]["callback_handler"]
            agent_run_id = agent_monitor._runtime.agent_run_id

            # Add a tool call directly to repository
            tool_call = AgentsRuntimeToolCall(
                tool_use_id="tool-1",
                tool_name="calculator",
                tool_input={"expression": "2+2"},
                status="success",
            )
            repo.update_agent_runtime_tool_call(agent_id, agent_run_id, tool_call)

            # Verify agent directory was created
            agent_dir = os.path.join(tmpdir, f"agent_{agent_id}")
            assert os.path.exists(agent_dir)

            # Load in new manager with same repository
            manager2 = AgentsMonitorManager(runtime_repo=repo)

            monitors = manager2.list_agent_runtimes(agent_id)
            assert len(monitors) == 1

            # Load the agent runtime monitor
            loaded_monitor = manager2.get_agent_runtime(agent_id, agent_run_id)
            assert loaded_monitor is not None

            # Load tool calls through the repository
            loaded_tool_calls = repo.list_agent_runtime_tool_calls(
                agent_id, agent_run_id
            )
            assert len(loaded_tool_calls) == 1
            assert loaded_tool_calls[0].tool_name == "calculator"

    def test_list_tool_calls(self):
        """Test listing tool calls for an agent runtime"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            manager = AgentsMonitorManager(runtime_repo=repo)

            # Mock tools retriever and agent creator
            mock_tools_retriever = Mock()
            mock_tools_retriever.retrieve.return_value = []
            mock_agent_creator = Mock(return_value=MagicMock())
            mock_agent_creator.name = "TestAgent"

            _ = manager.create_agent_runtime(
                query="Test query",
                tools_retriever=mock_tools_retriever,
                agent_creator=mock_agent_creator,
            )
            agent_id = mock_agent_creator.call_args[1]["agent_id"]
            agent_monitor = mock_agent_creator.call_args[1]["callback_handler"]
            agent_run_id = agent_monitor._runtime.agent_run_id

            # Add some tool calls
            tool_call1 = AgentsRuntimeToolCall(
                tool_use_id="tool-1", tool_name="calculator"
            )
            tool_call2 = AgentsRuntimeToolCall(tool_use_id="tool-2", tool_name="search")
            repo.update_agent_runtime_tool_call(agent_id, agent_run_id, tool_call1)
            repo.update_agent_runtime_tool_call(agent_id, agent_run_id, tool_call2)

            # Get agent runtime monitor and list tool calls through the repository
            monitor = manager.get_agent_runtime(agent_id, agent_run_id)
            assert monitor is not None

            tool_calls = repo.list_agent_runtime_tool_calls(agent_id, agent_run_id)
            assert len(tool_calls) == 2

            tool_call_ids = {tc.tool_use_id for tc in tool_calls}
            assert "tool-1" in tool_call_ids
            assert "tool-2" in tool_call_ids

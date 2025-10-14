#!/usr/bin/env python3
"""
Tests for FileAgentsRuntimeRepository functionality.
"""

import tempfile
from datetime import datetime

from fivcadvisor.agents.types import AgentsRuntime, AgentsRuntimeToolCall, AgentsStatus
from fivcadvisor.agents.types.repositories.files import FileAgentsRuntimeRepository
from fivcadvisor.utils import OutputDir


class TestFileAgentsRuntimeRepository:
    """Tests for FileAgentsRuntimeRepository class"""

    def test_initialization(self):
        """Test repository initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            assert repo.output_dir == output_dir
            assert repo.base_path.exists()
            assert repo.base_path.is_dir()

    def test_update_and_get_agent(self):
        """Test creating and retrieving an agent runtime"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent runtime
            agent = AgentsRuntime(
                agent_id="test-agent-123",
                agent_name="TestAgent",
                status=AgentsStatus.EXECUTING,
                started_at=datetime(2024, 1, 1, 12, 0, 0),
            )

            # Save agent
            repo.update_agent_runtime("test-agent-123", agent)

            # Verify agent file exists
            agent_file = repo._get_run_file("test-agent-123", agent.agent_run_id)
            assert agent_file.exists()

            # Retrieve agent
            retrieved_agent = repo.get_agent_runtime(
                "test-agent-123", agent.agent_run_id
            )
            assert retrieved_agent is not None
            assert retrieved_agent.agent_id == "test-agent-123"
            assert retrieved_agent.agent_name == "TestAgent"
            assert retrieved_agent.status == AgentsStatus.EXECUTING
            assert retrieved_agent.started_at == datetime(2024, 1, 1, 12, 0, 0)

    def test_get_nonexistent_agent(self):
        """Test retrieving an agent that doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Try to get non-existent agent
            agent = repo.get_agent_runtime("nonexistent-agent", "nonexistent-run")
            assert agent is None

    def test_delete_agent(self):
        """Test deleting an agent runtime"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent
            agent = AgentsRuntime(
                agent_id="test-agent-456",
                agent_name="TestAgent",
            )
            repo.update_agent_runtime("test-agent-456", agent)

            # Verify agent exists
            assert (
                repo.get_agent_runtime("test-agent-456", agent.agent_run_id) is not None
            )

            # Delete agent
            repo.delete_agent_runtime("test-agent-456", agent.agent_run_id)

            # Verify agent is deleted
            assert repo.get_agent_runtime("test-agent-456", agent.agent_run_id) is None
            assert not repo._get_run_dir("test-agent-456", agent.agent_run_id).exists()

    def test_update_and_get_tool_call(self):
        """Test creating and retrieving a tool call"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent first
            agent = AgentsRuntime(
                agent_id="test-agent-789",
                agent_name="TestAgent",
            )
            repo.update_agent_runtime("test-agent-789", agent)

            # Create a tool call
            tool_call = AgentsRuntimeToolCall(
                tool_use_id="tool-call-1",
                tool_name="TestTool",
                tool_input={"param": "value"},
                status="pending",
                started_at=datetime(2024, 1, 1, 12, 0, 0),
            )

            # Save tool call
            repo.update_agent_runtime_tool_call(
                "test-agent-789", agent.agent_run_id, tool_call
            )

            # Verify tool call file exists
            tool_call_file = repo._get_tool_call_file(
                "test-agent-789", agent.agent_run_id, "tool-call-1"
            )
            assert tool_call_file.exists()

            # Retrieve tool call
            retrieved_tool_call = repo.get_agent_runtime_tool_call(
                "test-agent-789", agent.agent_run_id, "tool-call-1"
            )
            assert retrieved_tool_call is not None
            assert retrieved_tool_call.tool_use_id == "tool-call-1"
            assert retrieved_tool_call.tool_name == "TestTool"
            assert retrieved_tool_call.tool_input == {"param": "value"}
            assert retrieved_tool_call.status == "pending"

    def test_get_nonexistent_tool_call(self):
        """Test retrieving a tool call that doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Try to get non-existent tool call
            tool_call = repo.get_agent_runtime_tool_call(
                "test-agent-789", "nonexistent-run", "nonexistent-tool-call"
            )
            assert tool_call is None

    def test_list_tool_calls(self):
        """Test listing all tool calls for an agent runtime"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent
            agent = AgentsRuntime(
                agent_id="test-agent-999",
                agent_name="TestAgent",
            )
            repo.update_agent_runtime("test-agent-999", agent)

            # Create multiple tool calls
            tool_call1 = AgentsRuntimeToolCall(
                tool_use_id="tool-call-1",
                tool_name="Tool1",
                status="pending",
            )
            tool_call2 = AgentsRuntimeToolCall(
                tool_use_id="tool-call-2",
                tool_name="Tool2",
                status="success",
            )
            tool_call3 = AgentsRuntimeToolCall(
                tool_use_id="tool-call-3",
                tool_name="Tool3",
                status="error",
            )

            repo.update_agent_runtime_tool_call(
                "test-agent-999", agent.agent_run_id, tool_call1
            )
            repo.update_agent_runtime_tool_call(
                "test-agent-999", agent.agent_run_id, tool_call2
            )
            repo.update_agent_runtime_tool_call(
                "test-agent-999", agent.agent_run_id, tool_call3
            )

            # List tool calls
            tool_calls = repo.list_agent_runtime_tool_calls(
                "test-agent-999", agent.agent_run_id
            )
            assert len(tool_calls) == 3

            tool_call_ids = {tc.tool_use_id for tc in tool_calls}
            assert "tool-call-1" in tool_call_ids
            assert "tool-call-2" in tool_call_ids
            assert "tool-call-3" in tool_call_ids

    def test_list_tool_calls_for_nonexistent_agent(self):
        """Test listing tool calls for an agent that doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # List tool calls for non-existent agent
            tool_calls = repo.list_agent_runtime_tool_calls(
                "nonexistent-agent", "nonexistent-run"
            )
            assert tool_calls == []

    def test_update_existing_agent(self):
        """Test updating an existing agent runtime"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent
            agent = AgentsRuntime(
                agent_id="test-agent-update",
                agent_name="TestAgent",
                status=AgentsStatus.PENDING,
            )
            repo.update_agent_runtime("test-agent-update", agent)

            # Update agent status
            agent.status = AgentsStatus.COMPLETED
            agent.completed_at = datetime(2024, 1, 1, 13, 0, 0)
            repo.update_agent_runtime("test-agent-update", agent)

            # Retrieve and verify
            retrieved_agent = repo.get_agent_runtime(
                "test-agent-update", agent.agent_run_id
            )
            assert retrieved_agent.status == AgentsStatus.COMPLETED
            assert retrieved_agent.completed_at == datetime(2024, 1, 1, 13, 0, 0)

    def test_update_existing_tool_call(self):
        """Test updating an existing tool call"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent
            agent = AgentsRuntime(
                agent_id="test-agent-tool-update",
                agent_name="TestAgent",
            )
            repo.update_agent_runtime("test-agent-tool-update", agent)

            # Create a tool call
            tool_call = AgentsRuntimeToolCall(
                tool_use_id="tool-call-update",
                tool_name="TestTool",
                status="pending",
            )
            repo.update_agent_runtime_tool_call(
                "test-agent-tool-update", agent.agent_run_id, tool_call
            )

            # Update tool call
            tool_call.status = "success"
            tool_call.completed_at = datetime(2024, 1, 1, 14, 0, 0)
            tool_call.tool_result = {"result": "success"}
            repo.update_agent_runtime_tool_call(
                "test-agent-tool-update", agent.agent_run_id, tool_call
            )

            # Retrieve and verify
            retrieved_tool_call = repo.get_agent_runtime_tool_call(
                "test-agent-tool-update", agent.agent_run_id, "tool-call-update"
            )
            assert retrieved_tool_call.status == "success"
            assert retrieved_tool_call.completed_at == datetime(2024, 1, 1, 14, 0, 0)
            assert retrieved_tool_call.tool_result == {"result": "success"}

    def test_delete_agent_with_tool_calls(self):
        """Test deleting an agent that has tool calls"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent with tool calls
            agent = AgentsRuntime(
                agent_id="test-agent-with-tools",
                agent_name="TestAgent",
            )
            repo.update_agent_runtime("test-agent-with-tools", agent)

            tool_call1 = AgentsRuntimeToolCall(tool_use_id="tool-1", tool_name="Tool1")
            tool_call2 = AgentsRuntimeToolCall(tool_use_id="tool-2", tool_name="Tool2")
            repo.update_agent_runtime_tool_call(
                "test-agent-with-tools", agent.agent_run_id, tool_call1
            )
            repo.update_agent_runtime_tool_call(
                "test-agent-with-tools", agent.agent_run_id, tool_call2
            )

            # Verify agent and tool calls exist
            assert (
                repo.get_agent_runtime("test-agent-with-tools", agent.agent_run_id)
                is not None
            )
            assert (
                len(
                    repo.list_agent_runtime_tool_calls(
                        "test-agent-with-tools", agent.agent_run_id
                    )
                )
                == 2
            )

            # Delete agent
            repo.delete_agent_runtime("test-agent-with-tools", agent.agent_run_id)

            # Verify agent and tool calls are deleted
            assert (
                repo.get_agent_runtime("test-agent-with-tools", agent.agent_run_id)
                is None
            )
            assert (
                len(
                    repo.list_agent_runtime_tool_calls(
                        "test-agent-with-tools", agent.agent_run_id
                    )
                )
                == 0
            )

    def test_storage_structure(self):
        """Test that the storage structure matches the expected format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent with tool calls
            agent = AgentsRuntime(
                agent_id="structure-test",
                agent_name="StructureTestAgent",
            )
            repo.update_agent_runtime("structure-test", agent)

            tool_call = AgentsRuntimeToolCall(
                tool_use_id="tool-1", tool_name="TestTool"
            )
            repo.update_agent_runtime_tool_call(
                "structure-test", agent.agent_run_id, tool_call
            )

            # Verify directory structure
            agent_dir = repo._get_agent_dir("structure-test")
            assert agent_dir.exists()
            run_dir = repo._get_run_dir("structure-test", agent.agent_run_id)
            assert run_dir.exists()
            assert (run_dir / "run.json").exists()

            tool_calls_dir = repo._get_tool_calls_dir(
                "structure-test", agent.agent_run_id
            )
            assert tool_calls_dir.exists()
            assert (tool_calls_dir / "tool_call_tool-1.json").exists()

    def test_agent_with_streaming_text(self):
        """Test agent runtime with streaming text"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent with streaming text
            agent = AgentsRuntime(
                agent_id="streaming-agent",
                agent_name="StreamingAgent",
                streaming_text="This is streaming text...",
            )
            repo.update_agent_runtime("streaming-agent", agent)

            # Retrieve and verify
            retrieved_agent = repo.get_agent_runtime(
                "streaming-agent", agent.agent_run_id
            )
            assert retrieved_agent.streaming_text == "This is streaming text..."

    def test_agent_with_error(self):
        """Test agent runtime with error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent with error
            agent = AgentsRuntime(
                agent_id="error-agent",
                agent_name="ErrorAgent",
                status=AgentsStatus.FAILED,
                error="Something went wrong",
            )
            repo.update_agent_runtime("error-agent", agent)

            # Retrieve and verify
            retrieved_agent = repo.get_agent_runtime("error-agent", agent.agent_run_id)
            assert retrieved_agent.status == AgentsStatus.FAILED
            assert retrieved_agent.error == "Something went wrong"

    def test_tool_call_with_complex_input_and_result(self):
        """Test tool call with complex input and result data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Create an agent
            agent = AgentsRuntime(
                agent_id="complex-agent",
                agent_name="ComplexAgent",
            )
            repo.update_agent_runtime("complex-agent", agent)

            # Create a tool call with complex data
            tool_call = AgentsRuntimeToolCall(
                tool_use_id="complex-tool-call",
                tool_name="ComplexTool",
                tool_input={
                    "nested": {"data": [1, 2, 3]},
                    "string": "test",
                    "number": 42,
                },
                tool_result={
                    "status": "success",
                    "data": {"items": ["a", "b", "c"]},
                },
                status="success",
            )
            repo.update_agent_runtime_tool_call(
                "complex-agent", agent.agent_run_id, tool_call
            )

            # Retrieve and verify
            retrieved_tool_call = repo.get_agent_runtime_tool_call(
                "complex-agent", agent.agent_run_id, "complex-tool-call"
            )
            assert retrieved_tool_call.tool_input == {
                "nested": {"data": [1, 2, 3]},
                "string": "test",
                "number": 42,
            }
            assert retrieved_tool_call.tool_result == {
                "status": "success",
                "data": {"items": ["a", "b", "c"]},
            }

    def test_delete_nonexistent_agent(self):
        """Test deleting an agent that doesn't exist (should not raise error)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            # Delete non-existent agent (should not raise error)
            repo.delete_agent_runtime("nonexistent-agent", "nonexistent-run")

            # Verify nothing broke
            assert (
                repo.get_agent_runtime("nonexistent-agent", "nonexistent-run") is None
            )

    def test_list_agent_runtimes_chronological_order(self):
        """Test that list_agent_runtimes returns runtimes in chronological order"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            repo = FileAgentsRuntimeRepository(output_dir=output_dir)

            agent_id = "test-agent-chronological"

            # Create multiple runtimes with different timestamps
            # Note: agent_run_id is a timestamp string, so we create them with explicit values
            runtime1 = AgentsRuntime(
                agent_id=agent_id,
                agent_name="TestAgent",
                agent_run_id="1000.0",  # Earliest
                status=AgentsStatus.COMPLETED,
            )
            runtime2 = AgentsRuntime(
                agent_id=agent_id,
                agent_name="TestAgent",
                agent_run_id="2000.0",  # Middle
                status=AgentsStatus.COMPLETED,
            )
            runtime3 = AgentsRuntime(
                agent_id=agent_id,
                agent_name="TestAgent",
                agent_run_id="3000.0",  # Latest
                status=AgentsStatus.COMPLETED,
            )

            # Save in random order
            repo.update_agent_runtime(agent_id, runtime2)
            repo.update_agent_runtime(agent_id, runtime1)
            repo.update_agent_runtime(agent_id, runtime3)

            # List runtimes
            runtimes = repo.list_agent_runtimes(agent_id)

            # Verify we got all 3
            assert len(runtimes) == 3

            # Verify they are in chronological order (increasing agent_run_id)
            assert runtimes[0].agent_run_id == "1000.0"
            assert runtimes[1].agent_run_id == "2000.0"
            assert runtimes[2].agent_run_id == "3000.0"

            # Verify the order is maintained
            for i in range(len(runtimes) - 1):
                assert runtimes[i].agent_run_id < runtimes[i + 1].agent_run_id

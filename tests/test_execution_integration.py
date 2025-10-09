#!/usr/bin/env python3
"""
Integration tests for run_executing_task

Tests the complete workflow integration without requiring actual LLM calls.
"""

import sys
import pytest
import dotenv

from fivcadvisor import schemas, tasks, agents

dotenv.load_dotenv()


class TestExecutionTaskIntegration:
    """Integration tests for execution task"""

    def test_imports(self):
        """Test that all required imports work"""
        assert hasattr(tasks, "run_executing_task")
        assert hasattr(tasks, "run_planning_task")
        assert hasattr(tasks, "run_assessing_task")
        assert hasattr(agents, "create_generic_agent_swarm")
        assert hasattr(schemas, "TaskTeam")
        assert hasattr(tasks, "TaskTracer")
        assert hasattr(tasks, "TaskEvent")
        assert hasattr(tasks, "TaskStatus")

    def test_task_team_creation(self):
        """Test creating a TaskTeam"""
        team = schemas.TaskTeam(
            specialists=[
                schemas.TaskTeam.Specialist(
                    name="Researcher",
                    backstory="Expert researcher",
                    tools=["web_search"],
                ),
                schemas.TaskTeam.Specialist(
                    name="Analyst", backstory="Expert analyst", tools=["calculator"]
                ),
            ]
        )

        assert len(team.specialists) == 2
        assert team.specialists[0].name == "Researcher"
        assert team.specialists[1].name == "Analyst"
        assert "web_search" in team.specialists[0].tools
        assert "calculator" in team.specialists[1].tools

    def test_task_event_tracking(self):
        """Test TaskEvent tracking"""
        from datetime import datetime

        # Create task event
        event = tasks.TaskEvent(
            agent_name="TestAgent", agent_id="test-123", query="Test query"
        )

        assert event.query == "Test query"
        assert event.status == tasks.TaskStatus.IDLE
        assert event.agent_name == "TestAgent"

        # Update status
        event.status = tasks.TaskStatus.RUNNING
        event.started_at = datetime.now()

        assert event.status == tasks.TaskStatus.RUNNING
        assert event.started_at is not None
        assert event.is_running

        # Complete
        event.status = tasks.TaskStatus.COMPLETED
        event.completed_at = datetime.now()
        event.result = "Test result"

        assert event.status == tasks.TaskStatus.COMPLETED
        assert event.result == "Test result"
        assert event.is_completed
        assert event.duration is not None

    @pytest.mark.asyncio
    async def test_run_executing_task_signature(self):
        """Test run_executing_task function signature"""
        import inspect

        sig = inspect.signature(tasks.run_executing_task)
        params = list(sig.parameters.keys())

        assert "query" in params
        assert "plan" in params
        assert "tools_retriever" in params
        assert "kwargs" in params

        # Check it's async
        assert inspect.iscoroutinefunction(tasks.run_executing_task)

    def test_swarm_creator_signature(self):
        """Test create_generic_agent_swarm signature"""
        assert callable(agents.create_generic_agent_swarm)

        # Check it's in the agent creator registry
        retriever = agents.default_retriever
        creator = retriever.get("Generic Swarm")

        assert creator is not None
        assert creator.name == "Generic Swarm"

    def test_workflow_components(self):
        """Test that all workflow components exist"""
        # Assessment
        assert hasattr(tasks, "run_assessing_task")
        assert callable(tasks.run_assessing_task)

        # Planning
        assert hasattr(tasks, "run_planning_task")
        assert callable(tasks.run_planning_task)

        # Execution
        assert hasattr(tasks, "run_executing_task")
        assert callable(tasks.run_executing_task)

        # Schemas
        assert hasattr(schemas, "TaskAssessment")
        assert hasattr(schemas, "TaskTeam")

        # Task tracking
        assert hasattr(tasks, "TaskTracer")
        assert hasattr(tasks, "TaskEvent")
        assert hasattr(tasks, "TaskStatus")

    def test_task_state_enum(self):
        """Test TaskStatus enum"""
        assert tasks.TaskStatus.IDLE == "idle"
        assert tasks.TaskStatus.STARTING == "starting"
        assert tasks.TaskStatus.RUNNING == "running"
        assert tasks.TaskStatus.COMPLETED == "completed"
        assert tasks.TaskStatus.FAILED == "failed"

    def test_exports(self):
        """Test that functions are properly exported"""
        # Tasks module
        assert "run_executing_task" in tasks.__all__
        assert "run_planning_task" in tasks.__all__
        assert "run_assessing_task" in tasks.__all__

        # Agents module
        assert "create_generic_agent_swarm" in agents.__all__
        assert "create_default_agent" in agents.__all__


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Integration Tests")
    print("=" * 60)

    test_suite = TestExecutionTaskIntegration()

    tests = [
        ("Imports", test_suite.test_imports),
        ("TaskTeam Creation", test_suite.test_task_team_creation),
        ("TaskExecution Tracking", test_suite.test_task_execution_tracking),
        ("TaskExecution with Team", test_suite.test_task_execution_with_team),
        ("Swarm Creator Signature", test_suite.test_swarm_creator_signature),
        ("Workflow Components", test_suite.test_workflow_components),
        ("TaskStatus Enum", test_suite.test_task_status_enum),
        ("Exports", test_suite.test_exports),
    ]

    results = []

    for name, test_func in tests:
        try:
            print(f"\n{'=' * 60}")
            print(f"Test: {name}")
            print(f"{'=' * 60}")

            test_func()

            print("✅ PASSED")
            results.append((name, True, None))

        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append((name, False, str(e)))

    # Print summary
    print(f"\n{'=' * 60}")
    print("Test Summary")
    print(f"{'=' * 60}")

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for name, success, error in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
        if error:
            print(f"   Error: {error}")

    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'=' * 60}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_tests())

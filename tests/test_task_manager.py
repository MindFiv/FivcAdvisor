#!/usr/bin/env python3
"""
Tests for TaskManager functionality.
"""

import os
import tempfile
from unittest.mock import Mock, patch

from fivcadvisor.tasks.types import TaskManager, TaskTracer, TaskEvent, TaskStatus
from fivcadvisor import schemas
from fivcadvisor.utils import OutputDir


class TestTaskManager:
    """Tests for TaskManager class"""

    def test_initialization(self):
        """Test TaskManager initialization"""
        manager = TaskManager()

        assert manager.tracers == {}
        assert manager.output_dir is not None
        assert isinstance(manager.output_dir, OutputDir)
        assert manager.auto_save is False

    def test_initialization_with_output_dir(self):
        """Test TaskManager initialization with output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            manager = TaskManager(output_dir=output_dir)
            assert manager.output_dir == output_dir
            assert str(manager.output_dir) == str(output_dir)

    def test_create_task(self):
        """Test creating a task"""
        manager = TaskManager()

        plan = schemas.TaskTeam(
            specialists=[
                schemas.TaskTeam.Specialist(
                    name="TestAgent",
                    backstory="Test backstory",
                    tools=["calculator"],
                )
            ]
        )

        with patch("fivcadvisor.agents.create_generic_agent_swarm") as mock_create:
            mock_swarm = Mock()
            mock_create.return_value = mock_swarm

            swarm = manager.create_task(plan=plan)

            assert swarm == mock_swarm
            assert len(manager.tracers) == 1
            mock_create.assert_called_once()

    def test_list_tasks(self):
        """Test listing tasks"""
        manager = TaskManager()

        # Add some tracers manually
        tracer1 = TaskTracer()
        tracer2 = TaskTracer()
        manager.tracers[tracer1.id] = tracer1
        manager.tracers[tracer2.id] = tracer2

        tasks = manager.list_tasks()
        assert len(tasks) == 2
        assert tracer1 in tasks
        assert tracer2 in tasks

    def test_get_task(self):
        """Test getting a specific task"""
        manager = TaskManager()

        tracer = TaskTracer()
        manager.tracers[tracer.id] = tracer

        result = manager.get_task(tracer.id)
        assert result == tracer

        result = manager.get_task("nonexistent")
        assert result is None

    def test_delete_task(self):
        """Test deleting a task"""
        manager = TaskManager()

        tracer = TaskTracer()
        manager.tracers[tracer.id] = tracer

        assert len(manager.tracers) == 1

        manager.delete_task(tracer.id)

        assert len(manager.tracers) == 0

    def test_cleanup(self):
        """Test cleanup"""
        manager = TaskManager()

        tracer1 = TaskTracer()
        tracer2 = TaskTracer()
        manager.tracers[tracer1.id] = tracer1
        manager.tracers[tracer2.id] = tracer2

        assert len(manager.tracers) == 2

        manager.cleanup()

        assert len(manager.tracers) == 0

    def test_save_and_load(self):
        """Test saving and loading"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)

            # Create manager and add data
            manager1 = TaskManager(output_dir=output_dir)

            tracer = TaskTracer()
            event = TaskEvent(
                agent_name="Agent1",
                agent_id="1",
                query="test query",
                status=TaskStatus.COMPLETED,
            )
            tracer._events["1"] = event

            manager1.tracers[tracer.id] = tracer

            # Save - creates task_{tracer.id}.json
            manager1.save()

            # Verify file was created
            expected_file = os.path.join(tmpdir, f"task_{tracer.id}.json")
            assert os.path.exists(expected_file)

            # Load in new manager
            manager2 = TaskManager(output_dir=output_dir)

            assert len(manager2.tracers) == 1
            loaded_tracer = list(manager2.tracers.values())[0]
            assert len(loaded_tracer.list_events()) == 1
            loaded_event = loaded_tracer.list_events()[0]
            assert loaded_event.agent_name == "Agent1"
            assert loaded_event.query == "test query"

    def test_auto_save(self):
        """Test auto-save functionality"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = OutputDir(tmpdir)
            manager = TaskManager(output_dir=output_dir, auto_save=True)

            tracer = TaskTracer()
            tracer_id = tracer.id
            manager.tracers[tracer_id] = tracer

            # Manually save to create file
            tracer.save(os.path.join(tmpdir, f"task_{tracer_id}.json"))

            # Verify file was created
            expected_file = os.path.join(tmpdir, f"task_{tracer_id}.json")
            assert os.path.exists(expected_file)

            # Trigger auto-save by deleting
            manager.delete_task(tracer_id)

            # Verify file was deleted
            assert not os.path.exists(expected_file)

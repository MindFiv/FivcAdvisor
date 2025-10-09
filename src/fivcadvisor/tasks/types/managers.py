"""
Task manager for centralized task execution monitoring.

This module provides TaskManager class for managing and monitoring multiple tasks
across different agents and tracers.
"""

import os
from typing import List, Any, Optional, Callable, Dict

from fivcadvisor import agents, schemas, tools
from fivcadvisor.utils import OutputDir

from .tracers import TaskTracer, TaskEvent


class TaskManager(object):
    """
    Centralized task manager for monitoring and managing task execution.

    TaskManager provides a unified interface to:
    - Create and track tasks with agent swarms
    - Monitor task execution status
    - Persist task history to disk

    Usage:
        >>> from fivcadvisor.tasks.types import TaskManager
        >>> from fivcadvisor import schemas
        >>> from fivcadvisor.utils import OutputDir
        >>>
        >>> # Create manager with persistence
        >>> manager = TaskManager(output_dir=OutputDir("./data"))
        >>>
        >>> # Create a task
        >>> plan = schemas.TaskTeam(specialists=[...])
        >>> swarm = manager.create_task(plan=plan)
        >>>
        >>> # Execute task
        >>> result = await swarm.invoke_async("Your query")
        >>>
        >>> # View all tasks
        >>> tasks = manager.list_tasks()
        >>>
        >>> # Save to disk
        >>> manager.save()
    """

    def __init__(
        self, output_dir: Optional[OutputDir] = None, auto_save: bool = False, **kwargs
    ):
        """
        Initialize TaskManager.

        Args:
            output_dir: Optional OutputDir for persisting task data
            auto_save: If True, automatically save after each task event
        """
        self.tracers: Dict[str, TaskTracer] = {}
        self.output_dir = output_dir or OutputDir().subdir("tasks")
        self.auto_save = auto_save

        # Auto-load existing tracers
        self.load()

    def create_task(
        self,
        plan: schemas.TaskTeam,
        tools_retriever: Optional[tools.ToolsRetriever] = None,
        on_event: Optional[Callable[[TaskEvent], None]] = None,
        **kwargs: Any,
    ):
        """
        Create a new task with agent swarm and tracer.

        Args:
            plan: TaskTeam plan containing specialist agents
            tools_retriever: Optional tools retriever for agent tools
            on_event: Optional callback for task events
            **kwargs: Additional arguments to pass to the swarm

        Returns:
            Agent swarm instance
        """
        tracer = TaskTracer(on_event=on_event)
        kwargs["callback_handler"] = tracer

        task = agents.create_generic_agent_swarm(
            team=plan,
            tools_retriever=tools_retriever,
            **kwargs,
        )

        self.tracers[tracer.id] = tracer

        # Auto-save the new tracer
        if self.auto_save:
            tracer.save(os.path.join(str(self.output_dir), f"task_{tracer.id}.json"))

        return task

    def list_tasks(self) -> List[TaskTracer]:
        """
        Get list of all task tracers.

        Returns:
            List of TaskTracer instances
        """
        return list(self.tracers.values())

    def get_task(self, tracer_id: str) -> Optional[TaskTracer]:
        """
        Get a specific task tracer by ID.

        Args:
            tracer_id: Tracer ID to retrieve

        Returns:
            TaskTracer instance, or None if not found
        """
        return self.tracers.get(tracer_id)

    def delete_task(self, tracer_id: str) -> None:
        """
        Delete a task tracer and its file.

        Args:
            tracer_id: Tracer ID to delete
        """
        self.tracers.pop(tracer_id, None)

        # Delete the tracer's file
        if self.auto_save:
            filename = os.path.join(str(self.output_dir), f"task_{tracer_id}.json")
            if os.path.exists(filename):
                os.unlink(filename)

    def cleanup(self):
        """Clear all task tracers and their files."""
        if self.auto_save:
            self.output_dir.cleanup()

        self.tracers.clear()

    def save(self) -> None:
        """Save all tracers to individual files in output_dir."""
        for tracer in self.tracers.values():
            tracer.save(os.path.join(str(self.output_dir), f"task_{tracer.id}.json"))

    def load(self) -> None:
        """Load all tracers from output_dir."""
        self.tracers.clear()

        for filename in self.output_dir.glob("*.json"):
            try:
                tracer = TaskTracer.load(filename)
                self.tracers[tracer.id] = tracer
            except Exception as e:
                print(f"Warning: Failed to load {filename}: {e}")
                continue

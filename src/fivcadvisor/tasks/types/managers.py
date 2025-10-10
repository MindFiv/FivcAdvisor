"""
Task manager for centralized task execution monitoring.

This module provides TaskManager class for managing and monitoring multiple tasks
across different agent swarms. TaskManager uses TaskRuntimeRepository for persistence
and TaskMonitor for tracking individual task execution.

Key Features:
    - Create and track agent swarm tasks
    - Automatic persistence through repository pattern
    - Query task status and execution steps
    - Centralized task lifecycle management
"""

from typing import List, Any, Optional, Callable

from fivcadvisor import agents, schemas, tools
from fivcadvisor.tasks.types.monitors import (
    TaskMonitor,
    # TaskRuntime,
    TaskRuntimeStep,
    TaskRuntimeRepository,
)
from fivcadvisor.tasks.types.repositories.files import (
    FileTaskRuntimeRepository,
)


class TaskManager(object):
    """
    Centralized task manager for monitoring and managing task execution.

    TaskManager provides a unified interface to:
    - Create and track tasks with agent swarms
    - Monitor task execution status through TaskMonitor
    - Persist task history through TaskRuntimeRepository

    Usage:
        >>> from fivcadvisor.tasks.types import TaskManager
        >>> from fivcadvisor.tasks.types.repositories.files import FileTaskRuntimeRepository
        >>> from fivcadvisor import schemas, tools
        >>> from fivcadvisor.utils import OutputDir
        >>>
        >>> # Create manager with file-based persistence
        >>> repo = FileTaskRuntimeRepository(output_dir=OutputDir("./tasks"))
        >>> manager = TaskManager(runtime_repo=repo)
        >>>
        >>> # Create a task with monitoring
        >>> plan = schemas.TaskTeam(specialists=[...])
        >>> swarm = manager.create_task(
        ...     plan=plan,
        ...     tools_retriever=tools.default_retriever
        ... )
        >>>
        >>> # Execute task (automatically tracked and persisted)
        >>> result = await swarm.invoke_async("Your query")
        >>>
        >>> # View all tasks
        >>> tasks = manager.list_tasks()  # Returns list of TaskRuntime
        >>>
        >>> # Get specific task with monitor
        >>> task_monitor = manager.get_task(task_id)
        >>> steps = task_monitor.list_steps()
        >>>
        >>> # Delete a task
        >>> manager.delete_task(task_id)

    Default repository:
        If no repository is provided, TaskManager creates a default
        FileTaskRuntimeRepository with output_dir="./data".
    """

    def __init__(self, runtime_repo: Optional[TaskRuntimeRepository] = None, **kwargs):
        self._repo = runtime_repo or FileTaskRuntimeRepository()

    def create_task(
        self,
        plan: schemas.TaskTeam,
        tools_retriever: Optional[tools.ToolsRetriever] = None,
        on_event: Optional[Callable[[TaskRuntimeStep], None]] = None,
        **kwargs: Any,
    ):
        """
        Create a new task with agent swarm and monitor.

        Args:
            plan: TaskTeam plan containing specialist agents
            tools_retriever: Optional tools retriever for agent tools
            on_event: Optional callback for task events
            **kwargs: Additional arguments to pass to the swarm

        Returns:
            Agent swarm instance
        """
        task_monitor = TaskMonitor(
            on_event=on_event,
            runtime_repo=self._repo,
        )
        task = agents.create_generic_agent_swarm(
            team=plan,
            tools_retriever=tools_retriever,
            hooks=[task_monitor],
            **kwargs,
        )
        return task

    def list_tasks(self) -> List[TaskMonitor]:
        """
        Get list of all task monitors.

        Returns:
            List of TaskMonitor instances
        """
        task_runtimes = self._repo.list_tasks()
        return [
            TaskMonitor(runtime=runtime, runtime_repo=self._repo)
            for runtime in task_runtimes
        ]

    def get_task(
        self, task_id: str, on_event: Optional[Callable[[TaskRuntimeStep], None]] = None
    ) -> Optional[TaskMonitor]:
        task_runtime = self._repo.get_task(task_id)
        if not task_runtime:
            return None

        return TaskMonitor(
            runtime=task_runtime,
            runtime_repo=self._repo,
            on_event=on_event,
        )

    def delete_task(self, task_id: str) -> None:
        """
        Delete a task.

        Args:
            task_id: Task ID to delete
        """
        self._repo.delete_task(task_id)

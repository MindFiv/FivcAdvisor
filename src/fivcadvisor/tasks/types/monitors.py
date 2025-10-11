"""
Task execution monitor using Strands hooks.

This module provides TaskMonitor class for tracking Agent and MultiAgent execution state
through Strands' hook system. TaskMonitor can optionally persist execution data through
a TaskRuntimeRepository.

This module also provides TaskMonitorManager class for managing and monitoring multiple tasks
across different agent swarms. TaskMonitorManager uses TaskRuntimeRepository for persistence
and TaskMonitor for tracking individual task execution.

Key Features:
    - Hook-based execution tracking (recommended)
    - Optional persistence through repository pattern
    - Real-time step updates via callbacks
    - Automatic task and step lifecycle management
    - Backward compatibility with deprecated callback interface
    - Centralized task lifecycle management through TaskMonitorManager
"""

from functools import cached_property
from typing import Any, Optional, List, Callable
from datetime import datetime

from strands.hooks import (
    HookRegistry,
    HookEvent,
    AgentInitializedEvent,
    BeforeInvocationEvent,
    AfterInvocationEvent,
    MessageAddedEvent,
)

from fivcadvisor import schemas, tools
from fivcadvisor.tasks.types.base import (
    TaskStatus,
    TaskRuntime,
    TaskRuntimeStep,
)
from fivcadvisor.tasks.types.repositories import TaskRuntimeRepository


class TaskMonitor(object):
    """
    Task execution monitor using Strands hooks.

    Tracks Agent or MultiAgent execution state through hook events and provides
    optional persistence through a TaskRuntimeRepository.

    Usage with hooks (recommended):
        >>> from fivcadvisor.tasks.types import TaskMonitor
        >>> from fivcadvisor import agents, schemas
        >>>
        >>> # Create monitor with optional persistence
        >>> monitor = TaskMonitor()
        >>>
        >>> # Create agent swarm with monitor as hook
        >>> plan = schemas.TaskTeam(specialists=[...])
        >>> swarm = agents.create_generic_agent_swarm(
        ...     team=plan,
        ...     hooks=[monitor]
        ... )
        >>>
        >>> # Execute and monitor automatically tracks execution
        >>> result = await swarm.invoke_async("Your query")
        >>>
        >>> # Access execution steps
        >>> steps = monitor.list_steps()
        >>> for step in steps:
        ...     print(f"{step.agent_name}: {step.status}")

    Usage with persistence:
        >>> from fivcadvisor.tasks.types.repositories.files import FileTaskRuntimeRepository
        >>> from fivcadvisor.utils import OutputDir
        >>>
        >>> # Create repository
        >>> repo = FileTaskRuntimeRepository(output_dir=OutputDir("./tasks"))
        >>>
        >>> # Create monitor with persistence
        >>> monitor = TaskMonitor(runtime_repo=repo)
        >>>
        >>> # Task and steps are automatically persisted to disk
        >>> # Can be reloaded later
        >>> loaded_task = repo.get_task(monitor.id)
        >>> loaded_monitor = TaskMonitor(runtime=loaded_task, runtime_repo=repo)

    Event callbacks:
        You can register callbacks to be notified of task events:
        >>> def on_event(event: TaskRuntimeStep):
        ...     print(f"Event: {event.agent_name} - {event.status}")
        >>>
        >>> monitor = TaskMonitor(on_event=on_event)
    """

    @property
    def id(self):
        return self._runtime.id

    @cached_property
    def steps(self):
        if not self._runtime.steps and self._repo:
            steps = self._repo.list_steps(self.id)
            self._runtime.steps = {step.id: step for step in steps}
        return self._runtime.steps

    def __init__(
        self,
        on_event: Optional[Callable[[TaskRuntimeStep], None]] = None,
        runtime: Optional[TaskRuntime] = None,
        runtime_repo: Optional[TaskRuntimeRepository] = None,
    ):
        """
        Initialize TaskMonitor.

        Args:
            on_event: Callback when task event occurs (state changes, etc.)
        """
        self._runtime = runtime or TaskRuntime()
        self._repo = runtime_repo
        self._on_event = on_event

        if self._repo and not runtime:
            self._repo.update_task(self._runtime)

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(AgentInitializedEvent, self._on_hook_event)
        registry.add_callback(BeforeInvocationEvent, self._on_hook_event)
        registry.add_callback(AfterInvocationEvent, self._on_hook_event)
        registry.add_callback(MessageAddedEvent, self._on_hook_event)

    def _on_hook_event(self, event: HookEvent) -> None:
        agent = event.agent
        agent_id = agent.agent_id
        step = self.steps.get(agent.agent_id)
        if not step:
            # ensure event exists
            step = TaskRuntimeStep(
                id=agent_id,
                agent_name=agent.name,
                status=TaskStatus.EXECUTING,
                messages=[*agent.messages],
                started_at=datetime.now(),
            )
            self.steps[step.id] = step

        if isinstance(event, AfterInvocationEvent):
            step.completed_at = datetime.now()
            step.status = TaskStatus.COMPLETED

        elif isinstance(event, MessageAddedEvent):
            step.messages.append(event.message)

        if self._repo:
            self._repo.update_step(self.id, step)

        if self._on_event:
            self._on_event(step)

    def get_step(self, agent_id: str) -> Optional[TaskRuntimeStep]:
        """
        Get execution step for a specific agent.

        Args:
            agent_id: Agent ID (same as step ID) to retrieve

        Returns:
            TaskRuntimeStep for the agent, or None if not found
        """
        return self.steps.get(agent_id)

    def list_steps(self) -> List[TaskRuntimeStep]:
        """
        Get all execution steps for this task.

        Returns:
            List of all TaskRuntimeStep instances
        """
        return list(self.steps.values())

    def cleanup(self, step_id: Optional[str] = None) -> None:
        """
        Clean up task data.

        Args:
            step_id: Optional step ID to clean up. If None, cleans up all steps and the task.
        """
        if step_id:
            # Clean up specific step
            if step_id in self.steps:
                del self.steps[step_id]
                if self._repo:
                    # Note: FileTaskRuntimeRepository doesn't have delete_step method yet
                    # For now, we just remove from memory
                    pass
        else:
            # Clean up all steps and task
            self.steps.clear()

            if self._repo:
                self._repo.delete_task(self.id)

    def persist(self) -> None:
        """
        Manually persist task and all steps to the repository.

        This is useful when you want to ensure data is saved immediately.
        Note: Steps are automatically persisted when using hooks, so this
        is typically only needed when using the deprecated __call__ method.
        """
        if self._repo:
            self._repo.update_task(self._runtime)

            for step in self.steps.values():
                self._repo.update_step(self.id, step)


class TaskMonitorManager(object):
    """
    Centralized task monitor manager for monitoring and managing task execution.

    TaskMonitorManager provides a unified interface to:
    - Create and track tasks with agent swarms
    - Monitor task execution status through TaskMonitor
    - Persist task history through TaskRuntimeRepository

    Usage:
        >>> from fivcadvisor.tasks.types.monitors import TaskMonitorManager
        >>> from fivcadvisor.tasks.types.repositories.files import FileTaskRuntimeRepository
        >>> from fivcadvisor import schemas, tools
        >>> from fivcadvisor.utils import OutputDir
        >>>
        >>> # Create manager with file-based persistence
        >>> repo = FileTaskRuntimeRepository(output_dir=OutputDir("./tasks"))
        >>> manager = TaskMonitorManager(runtime_repo=repo)
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
        If no repository is provided, TaskMonitorManager creates a default
        FileTaskRuntimeRepository with output_dir="./data".
    """

    def __init__(
        self, runtime_repo: Optional["TaskRuntimeRepository"] = None, **kwargs
    ):
        from fivcadvisor.tasks.types.repositories.files import (
            FileTaskRuntimeRepository,
        )

        self._repo = runtime_repo or FileTaskRuntimeRepository()

    def create_task(
        self,
        plan: "schemas.TaskTeam",
        tools_retriever: Optional["tools.ToolsRetriever"] = None,
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
        from fivcadvisor import agents

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

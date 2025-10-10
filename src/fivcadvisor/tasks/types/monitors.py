"""
Task execution monitor using Strands hooks.

This module provides TaskMonitor class for tracking Agent and MultiAgent execution state
through Strands' hook system. TaskMonitor can optionally persist execution data through
a TaskRuntimeRepository.

Key Features:
    - Hook-based execution tracking (recommended)
    - Optional persistence through repository pattern
    - Real-time step updates via callbacks
    - Automatic task and step lifecycle management
    - Backward compatibility with deprecated callback interface
"""

from functools import cached_property
from typing import Any, Optional, List, Callable
from datetime import datetime

try:
    from warnings import deprecated
except ImportError:
    # Python < 3.13 doesn't have deprecated in warnings
    def deprecated(msg):
        """Fallback deprecated decorator for Python < 3.13"""

        def decorator(func):
            import warnings

            def wrapper(*args, **kwargs):
                warnings.warn(
                    f"{func.__name__} is deprecated: {msg}",
                    DeprecationWarning,
                    stacklevel=2,
                )
                return func(*args, **kwargs)

            return wrapper

        return decorator


from strands import Agent
from strands.hooks import (
    HookRegistry,
    HookEvent,
    AgentInitializedEvent,
    BeforeInvocationEvent,
    AfterInvocationEvent,
    MessageAddedEvent,
)

from .base import (
    TaskStatus,
    TaskRuntime,
    TaskRuntimeStep,
)
from .repositories import TaskRuntimeRepository


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

    @deprecated("Use register_hooks instead")
    def __call__(self, agent: Optional[Agent] = None, **kwargs: Any) -> None:
        """
        Callback handler for agent events.

        This method is called by the agent with various event types:
        - agent: Agent instance (provided as keyword argument by wrapper)
        - message: Message added during execution
        - result: Final result of execution
        - error: Error if execution failed

        Args:
            agent: Agent instance (optional for compatibility with Strands)
            **kwargs: Event data from the agent
        """
        # Agent must be provided
        if agent is None:
            return

        # Get agent_id directly from agent
        agent_id = agent.agent_id
        if not agent_id:
            return

        event = self.steps.get(agent_id)
        if not event:
            # ensure event exists
            event = TaskRuntimeStep(
                id=agent_id,
                agent_name=agent.name,
                status=TaskStatus.EXECUTING,
                messages=[*agent.messages],
                started_at=datetime.now(),
            )
            self.steps[agent_id] = event

        # Handle message events (store messages but don't trigger callback)
        if "message" in kwargs:
            event.messages.append(kwargs["message"])

        # Handle result
        elif "result" in kwargs:
            event.completed_at = datetime.now()
            event.status = TaskStatus.COMPLETED

            if self._on_event:
                self._on_event(event)

        # Handle error
        elif "error" in kwargs:
            event.completed_at = datetime.now()
            event.status = TaskStatus.FAILED
            event.error = str(kwargs["error"])

            if self._on_event:
                self._on_event(event)

        else:
            # Unknown event, trigger callback
            if self._on_event:
                self._on_event(event)

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

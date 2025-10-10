__all__ = [
    "TaskRuntime",
    "TaskRuntimeStep",
    "TaskRuntimeRepository",
]

from abc import ABC, abstractmethod
from typing import Optional, List

from fivcadvisor.tasks.types.base import TaskRuntime, TaskRuntimeStep


class TaskRuntimeRepository(ABC):
    """
    Abstract base class for task runtime data repositories.

    Defines the interface for persisting and retrieving task execution data.
    Implementations can use different storage backends (files, databases, etc.).

    Methods:
        update_task: Create or update a task's metadata
        get_task: Retrieve a task by ID
        delete_task: Delete a task and all its steps
        list_tasks: List all tasks in the repository
        update_step: Create or update an execution step
        get_step: Retrieve a specific step by task ID and step ID
        list_steps: List all steps for a task
    """

    @abstractmethod
    def update_task(self, task: TaskRuntime) -> None:
        """Create or update a task's metadata."""
        ...

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[TaskRuntime]:
        """Retrieve a task by ID."""
        ...

    @abstractmethod
    def delete_task(self, task_id: str) -> None:
        """Delete a task and all its steps."""
        ...

    @abstractmethod
    def list_tasks(self) -> List[TaskRuntime]:
        """List all tasks in the repository."""
        ...

    @abstractmethod
    def get_step(self, task_id: str, step_id: str) -> Optional[TaskRuntimeStep]:
        """Retrieve a specific step by task ID and step ID."""
        ...

    @abstractmethod
    def update_step(self, task_id: str, step: TaskRuntimeStep) -> None:
        """Create or update an execution step."""
        ...

    @abstractmethod
    def list_steps(self, task_id: str) -> List[TaskRuntimeStep]:
        """List all steps for a task."""
        ...

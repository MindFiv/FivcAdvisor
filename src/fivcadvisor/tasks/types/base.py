"""
Task runtime data models.

This module defines the core data models for task execution tracking:
    - TaskRuntimeStep: Individual agent execution step
    - TaskRuntime: Overall task execution state
    - TaskStatus: Execution status enumeration (imported from Strands)

These models use Pydantic for validation and serialization, making them
suitable for persistence and API communication.
"""

import uuid
from typing import Optional, List, Dict
from datetime import datetime

from pydantic import BaseModel, Field, computed_field
from strands.types.content import Message
from strands.multiagent.base import Status as TaskStatus


class TaskRuntimeStep(BaseModel):
    """
    Single task execution step record.

    Represents a single agent's execution within a task, tracking its status,
    timing, messages, and any errors that occurred.

    Attributes:
        id: Unique identifier for the step (also accessible as agent_id)
        agent_name: Name of the agent executing this step
        status: Current execution status (PENDING, EXECUTING, COMPLETED, FAILED)
        started_at: When the step started execution
        completed_at: When the step finished execution
        messages: List of messages exchanged during execution
        error: Error message if the step failed
    """

    model_config = {"arbitrary_types_allowed": True}

    id: str = Field(default=None, description="Unique identifier for the step")

    @computed_field
    @property
    def agent_id(self) -> str:  # same as id
        return self.id

    agent_name: str = Field(description="Name of the agent")

    status: TaskStatus = Field(
        default=TaskStatus.PENDING, description="Current execution status"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Step start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Step completion timestamp"
    )
    messages: List[Message] = Field(
        default_factory=list, description="Messages during execution"
    )
    error: Optional[str] = Field(default=None, description="Error message if failed")

    @computed_field
    @property
    def duration(self) -> Optional[float]:
        """Get execution duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @computed_field
    @property
    def is_running(self) -> bool:
        """Check if execution is currently runtime"""
        return self.status == TaskStatus.EXECUTING

    @computed_field
    @property
    def is_completed(self) -> bool:
        """Check if execution is completed (success or failure)"""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)


class TaskRuntime(BaseModel):
    """
    Task execution state and metadata.

    Represents the overall state of a task execution, including its status,
    timing, and all execution steps.

    Attributes:
        id: Unique task identifier (UUID)
        status: Current task status (PENDING, EXECUTING, COMPLETED, FAILED)
        started_at: When the task started execution
        completed_at: When the task finished execution
        steps: Dictionary mapping step IDs to TaskRuntimeStep instances
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique task ID"
    )

    @computed_field
    @property
    def task_id(self) -> str:  # same as id
        return self.id

    status: TaskStatus = Field(
        default=TaskStatus.PENDING, description="Current execution status"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Task start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Task completion timestamp"
    )
    steps: Dict[str, TaskRuntimeStep] = Field(
        default_factory=dict, description="Task execution steps"
    )

"""
Task execution tracer using Strands callbacks.

This module provides TaskTracer class for tracking Agent and MultiAgent execution state.
"""

import json
import uuid
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, computed_field
from strands import Agent
from strands.types.content import Message
from strands.agent import AgentResult


class TaskStatus(str, Enum):
    """Task execution state enumeration"""

    IDLE = "idle"  # Not executing
    STARTING = "starting"  # About to start
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"  # Failed with error


class TaskEvent(BaseModel):
    """Single task execution event record"""

    model_config = {"arbitrary_types_allowed": True}

    agent_name: str = Field(description="Name of the agent")
    agent_id: str = Field(default=None, description="Unique identifier for the agent")
    query: Optional[str] = Field(
        default=None, description="Query or prompt for the task"
    )
    status: TaskStatus = Field(
        default=TaskStatus.IDLE, description="Current execution status"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Task start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Task completion timestamp"
    )
    messages: List[Message] = Field(
        default_factory=list, description="Messages during execution"
    )
    error: Optional[str] = Field(default=None, description="Error message if failed")
    result: Optional[AgentResult] = Field(
        default=None, description="Task execution result"
    )

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
        """Check if execution is currently running"""
        return self.status == TaskStatus.RUNNING

    @computed_field
    @property
    def is_completed(self) -> bool:
        """Check if execution is completed (success or failure)"""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)


class TaskTracer(object):
    """
    Task execution tracer using Strands callbacks.

    Tracks Agent or MultiAgent execution state through callback events.

    Usage:
        >>> from fivcadvisor.tasks.types import TaskTracer
        >>> from fivcadvisor import agents
        >>>
        >>> # Create tracer
        >>> tracer = TaskTracer()
        >>>
        >>> # Create agent with tracer as callback handler
        >>> agent = agents.create_default_agent(callback_handler=tracer)
        >>>
        >>> # Execute agent
        >>> result = agent("What time is it?")
        >>>
        >>> # Get execution event for this agent
        >>> agent_id = agent.agent_id
        >>> event = tracer.get_event(agent_id)
        >>> print(f"Status: {event.status}")
        >>> print(f"Duration: {event.duration}s")

    Callbacks:
        You can register callbacks to be notified of task events:
        >>> def on_event(event: TaskEvent):
        ...     print(f"Event: {event.status}")
        >>>
        >>> tracer = TaskTracer(on_event=on_event)
    """

    @property
    def id(self):
        return self._id

    def __init__(
        self,
        on_event: Optional[Callable[[TaskEvent], None]] = None,
    ):
        """
        Initialize TaskTracer.

        Args:
            on_event: Callback when task event occurs (state changes, etc.)
        """
        self.on_event = on_event
        self._id = str(uuid.uuid4())
        self._events: Dict[str, TaskEvent] = {}  # agent_id -> TaskEvent

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

        event = self._events.get(agent_id)
        if not event:
            # ensure event exists
            event = TaskEvent(
                agent_name=agent.name,
                agent_id=agent_id,
                query=kwargs.get("query"),
                status=TaskStatus.RUNNING,
                started_at=datetime.now(),
            )
            self._events[agent_id] = event

        # Handle message events (store messages but don't trigger callback)
        if "message" in kwargs:
            event.messages.append(kwargs["message"])

        # Handle error
        elif "result" in kwargs:
            event.completed_at = datetime.now()
            event.status = TaskStatus.COMPLETED
            event.result = kwargs["result"]

            if self.on_event:
                self.on_event(event)

        # Handle result
        elif "error" in kwargs:
            event.completed_at = datetime.now()
            event.status = TaskStatus.FAILED
            event.error = str(kwargs["error"])

            if self.on_event:
                self.on_event(event)

        else:
            # Unknown event, trigger callback
            if self.on_event:
                self.on_event(event)

    def get_event(self, agent_id: str) -> Optional[TaskEvent]:
        """
        Get task event for a specific agent.

        Args:
            agent_id: Agent ID to get event for

        Returns:
            TaskEvent for the agent, or None if not found
        """
        return self._events.get(agent_id)

    def list_events(self) -> List[TaskEvent]:
        """
        Get all task events.

        Returns:
            List of all task events
        """
        return list(self._events.values())

    def cleanup(self, agent_id: Optional[str] = None) -> None:
        """
        Clear events.

        Args:
            agent_id: Optional agent ID. If provided, only clears event for that agent.
                     If None, clears all events.
        """
        if agent_id is not None:
            self._events.pop(agent_id, None)
        else:
            self._events.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "events": [
                event.model_dump(mode="json", exclude={"result"})
                for event in self._events.values()
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskTracer":
        events_data = data.get("events", [])
        events = []
        for event_data in events_data:
            # Handle both string and dict formats
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            events.append(TaskEvent(**event_data))

        tracer = cls()
        tracer._id = data.get("id", str(uuid.uuid4()))
        tracer._events = {e.agent_id: e for e in events}
        return tracer

    def save(self, filename: str) -> None:
        """Save tracer to file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filename: str) -> "TaskTracer":
        """Load tracer from file."""
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return cls.from_dict(data)

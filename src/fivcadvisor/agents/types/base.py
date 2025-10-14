"""
Agent runtime data models.

This module defines the core data models for single-agent execution tracking:
    - AgentsRuntimeToolCall: Individual tool call record
    - AgentsRuntime: Overall agent execution state
    - AgentsStatus: Execution status enumeration

These models use Pydantic for validation and serialization, making them
suitable for persistence and API communication.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, computed_field
from strands.types.content import Message


class AgentsStatus(str, Enum):
    """Agent execution status."""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentsRuntimeToolCall(BaseModel):
    """
    Single tool call record.

    Represents a single tool invocation during agent execution, tracking
    the tool use request and its result.

    Attributes:
        tool_use_id: Unique identifier for the tool call
        tool_name: Name of the tool being called
        tool_input: Input parameters passed to the tool
        tool_result: Result returned by the tool (if completed)
        status: Status of the tool call (success, error, pending)
        started_at: When the tool call started
        completed_at: When the tool call finished
        error: Error message if the tool call failed
    """

    @computed_field
    @property
    def id(self) -> str:  # same as tool use id
        return self.tool_use_id

    tool_use_id: str = Field(description="Unique tool call identifier")
    tool_name: str = Field(description="Name of the tool")
    tool_input: Dict[str, Any] = Field(
        default_factory=dict, description="Tool input parameters"
    )
    tool_result: Optional[Any] = Field(
        default=None, description="Tool execution result"
    )
    status: str = Field(default="pending", description="Tool call status")
    started_at: Optional[datetime] = Field(
        default=None, description="Tool call start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Tool call completion timestamp"
    )
    error: Optional[str] = Field(default=None, description="Error message if failed")

    @computed_field
    @property
    def duration(self) -> Optional[float]:
        """Get tool call duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @computed_field
    @property
    def is_completed(self) -> bool:
        """Check if tool call is completed."""
        return self.status in ("success", "error")


class AgentsRuntime(BaseModel):
    """
    Agent execution state and metadata.

    Represents the overall state of a single agent execution, including its status,
    timing, message, and tool calls.

    Attributes:
        id: Unique execution identifier (timestamp-based, computed from agent_run_id)
        agent_run_id: Unique run identifier (timestamp string for chronological ordering)
        agent_id: ID of the agent being executed
        agent_name: Name of the agent
        status: Current execution status (PENDING, EXECUTING, COMPLETED, FAILED)
        started_at: When the execution started
        completed_at: When the execution finished
        message: Current message being processed
        tool_calls: Dictionary mapping tool_use_id to AgentsRuntimeToolCall instances
        streaming_text: Accumulated streaming text from the agent
        error: Error message if execution failed
    """

    model_config = {"arbitrary_types_allowed": True}

    @computed_field
    @property
    def id(self) -> str:  # same as agent id
        return self.agent_run_id

    agent_run_id: str = Field(
        default_factory=lambda: str(datetime.now().timestamp()),
        description="Agent run identifier",
    )
    agent_id: Optional[str] = Field(default=None, description="Agent identifier")
    agent_name: Optional[str] = Field(default=None, description="Agent name")
    status: AgentsStatus = Field(
        default=AgentsStatus.PENDING, description="Current execution status"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Execution start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Execution completion timestamp"
    )
    query: Optional[str] = Field(
        default=None, description="User query for this agent run"
    )
    tool_calls: Dict[str, AgentsRuntimeToolCall] = Field(
        default_factory=dict, description="Tool calls made during execution"
    )
    message: Optional[Message] = Field(
        default=None, description="Current message being processed"
    )
    streaming_text: str = Field(default="", description="Accumulated streaming text")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    @computed_field
    @property
    def duration(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @computed_field
    @property
    def is_running(self) -> bool:
        """Check if execution is currently running."""
        return self.status == AgentsStatus.EXECUTING

    @computed_field
    @property
    def is_completed(self) -> bool:
        """Check if execution is completed (success or failure)."""
        return self.status in (AgentsStatus.COMPLETED, AgentsStatus.FAILED)

    @computed_field
    @property
    def tool_call_count(self) -> int:
        """Get total number of tool calls."""
        return len(self.tool_calls)

    @computed_field
    @property
    def successful_tool_calls(self) -> int:
        """Get number of successful tool calls."""
        return sum(1 for tc in self.tool_calls.values() if tc.status == "success")

    @computed_field
    @property
    def failed_tool_calls(self) -> int:
        """Get number of failed tool calls."""
        return sum(1 for tc in self.tool_calls.values() if tc.status == "error")

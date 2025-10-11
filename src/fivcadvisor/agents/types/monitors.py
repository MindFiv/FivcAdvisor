"""
Agent execution monitor for tracking single-agent execution.

This module provides AgentsMonitor class for tracking agent execution state
through callback events. AgentsMonitor captures streaming text chunks and
tool call events in an AgentsRuntime object, providing a framework-agnostic
interface for monitoring agent activity.

The monitor uses a unified callback pattern where a single on_event callback
receives the complete AgentsRuntime state after each event, allowing UI
components to access all execution data in one place.

Key Features:
    - Unified callback-based execution tracking via AgentsRuntime
    - Real-time streaming message accumulation
    - Tool call event capture with status tracking (toolUse and toolResult)
    - Framework-agnostic design (no UI dependencies)
    - Graceful error handling for callbacks
    - Cleanup method for resetting state between executions
"""

from datetime import datetime
from typing import Any, Optional, List, Callable, cast
from warnings import warn

from strands.types.content import Message
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolUse, ToolResult

from fivcadvisor.agents.types.base import (
    AgentsRuntime,
    AgentsRuntimeToolCall,
    AgentsStatus,
)


class AgentsMonitor(object):
    """
    Agent execution monitor for tracking single-agent execution.

    Tracks agent execution through callback events, capturing streaming text
    chunks and tool call events in an AgentsRuntime object. Provides real-time
    callbacks for UI updates while maintaining framework-agnostic design.

    The monitor uses a unified callback pattern where a single on_event callback
    receives the complete runtime state after each event, allowing UI components
    to access all execution data (streaming text, tool calls, status) in one place.

    Usage:
        >>> from fivcadvisor.agents.types import AgentsMonitor, AgentsRuntime
        >>> from fivcadvisor import agents
        >>>
        >>> # Create monitor with unified event callback
        >>> def on_event(runtime: AgentsRuntime):
        ...     # Access streaming text
        ...     print(f"Streaming: {runtime.streaming_text}", end="", flush=True)
        ...
        ...     # Access tool calls
        ...     for tool_call in runtime.tool_calls.values():
        ...         if tool_call.status == "executing":
        ...             print(f"Tool: {tool_call.tool_name}")
        >>>
        >>> monitor = AgentsMonitor(on_event=on_event)
        >>>
        >>> # Create agent with monitor as callback handler
        >>> agent = agents.create_companion_agent(callback_handler=monitor)
        >>>
        >>> # Execute and monitor automatically tracks execution
        >>> result = agent("What is 2+2?")
        >>>
        >>> # Access accumulated state via tool_calls property
        >>> tools = monitor.tool_calls
        >>>
        >>> # Reset for next execution with new callback
        >>> monitor.cleanup(on_event=on_event)

    Callback Signature:
        - on_event: Callable[[AgentsRuntime], None] - Called with complete runtime state
          after each streaming chunk or tool event
    """

    def __init__(
        self,
        runtime: Optional[AgentsRuntime] = None,
        on_event: Optional[Callable[[AgentsRuntime], None]] = None,
    ):
        """
        Initialize AgentsMonitor.

        Args:
            runtime: Optional AgentsRuntime instance to track execution state.
                     If not provided, a new AgentsRuntime will be created.
            on_event: Optional callback invoked after each event (streaming or tool).
                      Receives the complete AgentsRuntime state, allowing access to
                      streaming_text, tool_calls, and other execution metadata.
        """
        self._runtime = runtime or AgentsRuntime()
        self._on_event = on_event

    def __call__(self, **kwargs: Any) -> None:
        """
        Callback handler for agent events.

        This method is called by the agent with various event types:
        - event: StreamEvent with streaming text chunks
        - message: Message with tool use/result events

        Args:
            **kwargs: Event data from the agent
        """
        # Handle streaming events
        if "event" in kwargs:
            self._on_stream_event(cast(StreamEvent, kwargs["event"]))

        # Handle message events (tool calls)
        elif "message" in kwargs:
            self._on_message_event(kwargs["message"])

    def _on_stream_event(self, event: StreamEvent) -> None:
        """
        Handle streaming text events.

        Parses StreamEvent objects to extract text chunks and accumulates
        them into the runtime's streaming_text field. Invokes on_event callback
        if registered, passing the complete runtime state.

        Args:
            event: StreamEvent object from Strands containing contentBlockDelta
                   or contentBlockStart events
        """
        try:
            # Parse streaming event structure
            # StreamEvent format: {"contentBlockDelta": {"delta": {"text": str}}}
            if "contentBlockDelta" in event:
                chunk = event["contentBlockDelta"].get("delta", {})
                chunk = chunk and chunk.get("text")
                if chunk and isinstance(chunk, str):
                    # Accumulate text chunk
                    self._runtime.streaming_text += chunk
                    if self._on_event:
                        self._on_event(self._runtime)

            if "contentBlockStart" in event:
                # New message starting, clear the current message
                self._runtime.streaming_text = ""
                if self._on_event:
                    self._on_event(self._runtime)

        except Exception as e:
            # Gracefully handle parsing errors
            warn(
                f"Error parsing stream event: {e}",
                RuntimeWarning,
                stacklevel=2,
            )

    def _on_message_event(self, message: Message) -> None:
        """
        Handle message events containing tool calls.

        Parses Message objects to extract tool use and result events, creating
        or updating AgentsRuntimeToolCall instances in the runtime. Invokes
        on_event callback if registered, passing the complete runtime state.

        Args:
            message: Message object from Strands containing toolUse or toolResult
                     content blocks
        """
        try:
            # Parse message structure
            # Message format: {"role": str, "content": List[...]}
            content = message.get("content", [])

            for block in content:
                if "toolUse" in block:
                    tool_use = cast(ToolUse, block["toolUse"])
                    tool_use_id = tool_use.get("toolUseId")
                    self._runtime.tool_calls[tool_use_id] = AgentsRuntimeToolCall(
                        tool_use_id=tool_use_id,
                        tool_name=tool_use.get("name"),
                        tool_input=tool_use.get("input"),
                        started_at=datetime.now(),
                        status=AgentsStatus.EXECUTING,
                    )
                    if self._on_event:
                        self._on_event(self._runtime)

                if "toolResult" in block:
                    tool_result = cast(ToolResult, block["toolResult"])
                    tool_use_id = tool_result.get("toolUseId")
                    tool_call = self._runtime.tool_calls.get(tool_use_id)
                    if not tool_call:
                        warn(
                            f"Tool result received for unknown tool call: {tool_use_id}",
                            RuntimeWarning,
                            stacklevel=2,
                        )
                        continue

                    if tool_result.get("status") == "success":
                        tool_call.status = AgentsStatus.COMPLETED
                    else:
                        tool_call.status = AgentsStatus.FAILED

                    tool_call.tool_result = tool_result.get("content")
                    tool_call.completed_at = datetime.now()

                    if self._on_event:
                        self._on_event(self._runtime)

        except Exception as e:
            # Gracefully handle parsing errors
            warn(
                f"Error parsing message event: {e}",
                RuntimeWarning,
                stacklevel=2,
            )

    @property
    def tool_calls(self) -> List[AgentsRuntimeToolCall]:
        """
        Get list of all tool calls from the runtime.

        Returns:
            List of AgentsRuntimeToolCall instances representing all tool
            invocations during the current execution.
        """
        return list(self._runtime.tool_calls.values())

    def cleanup(
        self,
        runtime: Optional[AgentsRuntime] = None,
        on_event: Optional[Callable[[AgentsRuntime], None]] = None,
    ) -> None:
        """
        Reset monitor state for a new execution.

        Replaces the current runtime with a new one (or the provided runtime)
        and optionally updates the event callback. This is typically called
        before starting a new agent execution to clear previous state.

        Args:
            runtime: Optional new AgentsRuntime instance. If not provided,
                     a fresh AgentsRuntime will be created.
            on_event: Optional new event callback. If not provided, the
                      callback will be cleared (set to None).
        """
        self._runtime = runtime or AgentsRuntime()
        self._on_event = on_event

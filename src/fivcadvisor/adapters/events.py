"""
LangChain event system adapter for Strands hooks compatibility.

This module provides an event bus system that replaces Strands hooks,
enabling event-driven architecture for agent execution monitoring.
"""

from typing import Any, Dict, List, Callable, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Event types for agent execution lifecycle."""

    AGENT_INITIALIZED = "agent_initialized"
    BEFORE_INVOCATION = "before_invocation"
    AFTER_INVOCATION = "after_invocation"
    MESSAGE_ADDED = "message_added"
    TOOL_CALLED = "tool_called"
    TOOL_RESULT = "tool_result"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Event:
    """Base event class for all events."""

    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.event_type}, timestamp={self.timestamp})"


class AgentInitializedEvent(Event):
    """Event fired when an agent is initialized."""

    def __init__(
        self, agent_id: Optional[str] = None, agent_name: Optional[str] = None, **kwargs
    ):
        super().__init__(event_type=EventType.AGENT_INITIALIZED, **kwargs)
        self.agent_id = agent_id
        self.agent_name = agent_name


class BeforeInvocationEvent(Event):
    """Event fired before agent invocation."""

    def __init__(
        self, agent_id: Optional[str] = None, query: Optional[str] = None, **kwargs
    ):
        super().__init__(event_type=EventType.BEFORE_INVOCATION, **kwargs)
        self.agent_id = agent_id
        self.query = query


class AfterInvocationEvent(Event):
    """Event fired after agent invocation."""

    def __init__(
        self, agent_id: Optional[str] = None, result: Optional[Any] = None, **kwargs
    ):
        super().__init__(event_type=EventType.AFTER_INVOCATION, **kwargs)
        self.agent_id = agent_id
        self.result = result


class MessageAddedEvent(Event):
    """Event fired when a message is added."""

    def __init__(
        self, message: Optional[str] = None, role: Optional[str] = None, **kwargs
    ):
        super().__init__(event_type=EventType.MESSAGE_ADDED, **kwargs)
        self.message = message
        self.role = role


class ToolCalledEvent(Event):
    """Event fired when a tool is called."""

    def __init__(
        self,
        tool_name: Optional[str] = None,
        tool_input: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(event_type=EventType.TOOL_CALLED, **kwargs)
        self.tool_name = tool_name
        self.tool_input = tool_input


class ToolResultEvent(Event):
    """Event fired when a tool returns a result."""

    def __init__(
        self,
        tool_name: Optional[str] = None,
        tool_result: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(event_type=EventType.TOOL_RESULT, **kwargs)
        self.tool_name = tool_name
        self.tool_result = tool_result


class ErrorOccurredEvent(Event):
    """Event fired when an error occurs."""

    def __init__(
        self,
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(event_type=EventType.ERROR_OCCURRED, **kwargs)
        self.error_message = error_message
        self.error_type = error_type


class EventBus:
    """
    Event bus for managing event subscriptions and dispatching.

    This class replaces Strands HookRegistry, providing a similar interface
    for event-driven architecture.
    """

    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []

    def subscribe(
        self,
        event_type: EventType,
        callback: Callable[[Event], None],
    ) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to subscribe to
            callback: Function to call when event is fired
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(
        self,
        event_type: EventType,
        callback: Callable[[Event], None],
    ) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: The type of event to unsubscribe from
            callback: The callback function to remove
        """
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def emit(self, event: Event) -> None:
        """
        Emit an event to all subscribers.

        Args:
            event: The event to emit
        """
        self._event_history.append(event)

        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")

    def get_history(self) -> List[Event]:
        """
        Get the event history.

        Returns:
            List of all events that have been emitted
        """
        return self._event_history.copy()

    def clear_history(self) -> None:
        """Clear the event history."""
        self._event_history.clear()

    def clear_subscribers(self) -> None:
        """Clear all subscribers."""
        self._subscribers.clear()

    def __repr__(self) -> str:
        return f"EventBus(subscribers={len(self._subscribers)}, events={len(self._event_history)})"


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """
    Get the global event bus instance.

    Returns:
        The global EventBus instance
    """
    return _event_bus


def emit_event(event: Event) -> None:
    """
    Emit an event using the global event bus.

    Args:
        event: The event to emit
    """
    _event_bus.emit(event)


def subscribe_to_event(
    event_type: EventType,
    callback: Callable[[Event], None],
) -> None:
    """
    Subscribe to an event type using the global event bus.

    Args:
        event_type: The type of event to subscribe to
        callback: Function to call when event is fired
    """
    _event_bus.subscribe(event_type, callback)

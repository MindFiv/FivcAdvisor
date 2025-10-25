"""
Hook system for monitoring agent and task execution.

This module provides event classes and hook registry for tracking
agent lifecycle and execution events.
"""

from typing import Any, Callable, Dict, List, Type, Optional
from datetime import datetime
from langchain_core.messages import BaseMessage


class HookEvent:
    """Base class for hook events."""

    def __init__(self, agent: Any = None, **kwargs: Any):
        """Initialize hook event."""
        self.agent = agent
        self.timestamp = datetime.now()
        for key, value in kwargs.items():
            setattr(self, key, value)


class AgentInitializedEvent(HookEvent):
    """Event fired when an agent is initialized."""

    pass


class BeforeInvocationEvent(HookEvent):
    """Event fired before agent invocation."""

    pass


class AfterInvocationEvent(HookEvent):
    """Event fired after agent invocation."""

    pass


class MessageAddedEvent(HookEvent):
    """Event fired when a message is added."""

    def __init__(
        self, agent: Any = None, message: Optional[BaseMessage] = None, **kwargs: Any
    ):
        """Initialize message added event."""
        super().__init__(agent=agent, **kwargs)
        self.message = message


class HookRegistry:
    """
    Registry for managing hook callbacks.

    Allows registering callbacks for different event types and firing
    events to all registered callbacks.
    """

    def __init__(self):
        """Initialize hook registry."""
        self._callbacks: Dict[Type[HookEvent], List[Callable]] = {}

    def add_callback(self, event_type: Type[HookEvent], callback: Callable) -> None:
        """
        Register a callback for an event type.

        Args:
            event_type: The event class to listen for
            callback: The callback function to invoke
        """
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)

    def remove_callback(self, event_type: Type[HookEvent], callback: Callable) -> None:
        """
        Unregister a callback for an event type.

        Args:
            event_type: The event class
            callback: The callback function to remove
        """
        if event_type in self._callbacks:
            self._callbacks[event_type].remove(callback)

    def fire(self, event: HookEvent) -> None:
        """
        Fire an event to all registered callbacks.

        Args:
            event: The event to fire
        """
        event_type = type(event)
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    # Log error but don't stop other callbacks
                    import warnings

                    warnings.warn(
                        f"Error in hook callback: {e}",
                        RuntimeWarning,
                        stacklevel=2,
                    )

    def clear(self) -> None:
        """Clear all registered callbacks."""
        self._callbacks.clear()

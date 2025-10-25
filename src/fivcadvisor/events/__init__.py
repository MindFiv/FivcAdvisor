"""
Event system for FivcAdvisor.

This module provides event classes and hook registry for monitoring
agent and task execution.
"""

from fivcadvisor.events.hooks import (
    HookRegistry,
    HookEvent,
    AgentInitializedEvent,
    BeforeInvocationEvent,
    AfterInvocationEvent,
    MessageAddedEvent,
)
from fivcadvisor.events.types import (
    StreamEvent,
    MessageDictAdapter,
    AgentResult,
    SlidingWindowConversationManager,
)

__all__ = [
    "HookRegistry",
    "HookEvent",
    "AgentInitializedEvent",
    "BeforeInvocationEvent",
    "AfterInvocationEvent",
    "MessageAddedEvent",
    "StreamEvent",
    "MessageDictAdapter",
    "AgentResult",
    "SlidingWindowConversationManager",
]

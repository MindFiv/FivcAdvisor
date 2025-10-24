"""
Adapters for LangChain/LangGraph integration.

This module provides adapters to migrate from Strands Agents to LangChain/LangGraph.
"""

__all__ = [
    # Multi-agent
    "create_langchain_swarm",
    "LangGraphSwarmAdapter",
    # Models
    "create_langchain_model",
    "create_default_langchain_model",
    "create_chat_langchain_model",
    "create_reasoning_langchain_model",
    "create_coding_langchain_model",
    "create_openai_model",
    "create_ollama_model",
    "create_litellm_model",
    # Tools
    "convert_strands_tool_to_langchain",
    "convert_strands_tools_to_langchain",
    "create_tool_adapter",
    "is_strands_tool",
    "is_langchain_tool",
    "ToolAdapter",
    "adapt_tool",
    "adapt_tools",
    # Events
    "EventType",
    "Event",
    "AgentInitializedEvent",
    "BeforeInvocationEvent",
    "AfterInvocationEvent",
    "MessageAddedEvent",
    "ToolCalledEvent",
    "ToolResultEvent",
    "ErrorOccurredEvent",
    "EventBus",
    "get_event_bus",
    "emit_event",
    "subscribe_to_event",
]

from fivcadvisor.adapters.multiagent import (
    create_langchain_swarm,
    LangGraphSwarmAdapter,
)

from fivcadvisor.adapters.models import (
    create_langchain_model,
    create_default_langchain_model,
    create_chat_langchain_model,
    create_reasoning_langchain_model,
    create_coding_langchain_model,
    create_openai_model,
    create_ollama_model,
    create_litellm_model,
)

from fivcadvisor.adapters.tools import (
    convert_strands_tool_to_langchain,
    convert_strands_tools_to_langchain,
    create_tool_adapter,
    is_strands_tool,
    is_langchain_tool,
    ToolAdapter,
    adapt_tool,
    adapt_tools,
)

from fivcadvisor.adapters.events import (
    EventType,
    Event,
    AgentInitializedEvent,
    BeforeInvocationEvent,
    AfterInvocationEvent,
    MessageAddedEvent,
    ToolCalledEvent,
    ToolResultEvent,
    ErrorOccurredEvent,
    EventBus,
    get_event_bus,
    emit_event,
    subscribe_to_event,
)


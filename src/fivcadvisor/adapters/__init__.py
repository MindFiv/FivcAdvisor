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


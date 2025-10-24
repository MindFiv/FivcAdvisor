"""
Adapters for LangChain/LangGraph integration.

This module provides adapters to migrate from Strands Agents to LangChain/LangGraph.
"""

__all__ = [
    "create_langchain_swarm",
    "LangGraphSwarmAdapter",
]

from fivcadvisor.adapters.multiagent import (
    create_langchain_swarm,
    LangGraphSwarmAdapter,
)


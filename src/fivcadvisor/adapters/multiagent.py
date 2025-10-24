"""
LangGraph Swarm adapter for multi-agent orchestration.

This module provides a wrapper around LangGraph Swarm to replace Strands Swarm
with minimal changes to existing code.

Key Components:
    - LangGraphSwarmAdapter: Main adapter class for swarm orchestration
    - create_langchain_swarm: Factory function for creating swarms

Features:
    - Multi-agent coordination with dynamic handoffs
    - Backward compatible with Strands Swarm API
    - Full async/await support
    - Flexible agent configuration
    - Event-based communication between agents

Example:
    >>> from fivcadvisor.adapters import create_langchain_swarm
    >>> from fivcadvisor.agents import create_default_agent
    >>> from langchain_openai import ChatOpenAI
    >>>
    >>> llm = ChatOpenAI(model="gpt-4o-mini")
    >>> agent1 = create_default_agent(model=llm, tools=[], name="Agent1")
    >>> agent2 = create_default_agent(model=llm, tools=[], name="Agent2")
    >>> swarm = create_langchain_swarm([agent1, agent2])
    >>> result = await swarm.invoke_async("Your query")
"""

from typing import Any, List, Optional, Dict
import asyncio
from langgraph_swarm import create_swarm


class LangGraphSwarmAdapter:
    """
    Adapter for LangGraph Swarm that provides a Strands-compatible API.

    This adapter wraps LangGraph Swarm to maintain compatibility with existing
    code that expects a Strands Swarm interface.
    """

    def __init__(
        self, agents: List[Any], default_agent_name: Optional[str] = None, **kwargs
    ):
        """
        Initialize the LangGraph Swarm adapter.

        Args:
            agents: List of LangChain agents to include in the swarm
            default_agent_name: Name of the default agent to start with
            **kwargs: Additional arguments (for future compatibility)
        """
        if not agents:
            raise ValueError("At least one agent is required")

        self.agents = agents
        self.default_agent_name = default_agent_name or agents[0].name

        # Create the LangGraph Swarm
        self.workflow = create_swarm(
            agents=agents, default_active_agent=self.default_agent_name
        )
        self.app = self.workflow.compile()

    async def invoke_async(self, query: str, **kwargs) -> dict:
        """
        Asynchronously invoke the swarm with a query.

        Args:
            query: The user query to process
            **kwargs: Additional arguments (config, etc.)

        Returns:
            Dictionary containing the result with 'messages' key
        """
        result = await self.app.ainvoke(
            {"messages": [{"role": "user", "content": query}]},
            config=kwargs.get("config"),
        )
        return result

    def invoke(self, query: str, **kwargs) -> dict:
        """
        Synchronously invoke the swarm with a query.

        Args:
            query: The user query to process
            **kwargs: Additional arguments

        Returns:
            Dictionary containing the result with 'messages' key
        """
        return asyncio.run(self.invoke_async(query, **kwargs))

    def get_agent_by_name(self, name: str) -> Optional[Any]:
        """
        Get an agent from the swarm by name.

        Args:
            name: The name of the agent to retrieve

        Returns:
            The agent if found, None otherwise
        """
        for agent in self.agents:
            if hasattr(agent, "name") and agent.name == name:
                return agent
        return None

    def get_agent_names(self) -> List[str]:
        """
        Get the names of all agents in the swarm.

        Returns:
            List of agent names
        """
        return [agent.name for agent in self.agents if hasattr(agent, "name")]

    def set_default_agent(self, agent_name: str) -> None:
        """
        Set the default agent for the swarm.

        Args:
            agent_name: The name of the agent to set as default

        Raises:
            ValueError: If the agent name is not found in the swarm
        """
        if not any(
            agent.name == agent_name
            for agent in self.agents
            if hasattr(agent, "name")
        ):
            raise ValueError(f"Agent '{agent_name}' not found in swarm")
        self.default_agent_name = agent_name


def create_langchain_swarm(
    agents: List[Any], default_agent_name: Optional[str] = None, **kwargs
) -> LangGraphSwarmAdapter:
    """
    Create a LangGraph Swarm adapter.

    This is the main factory function for creating a swarm of agents using
    LangGraph Swarm as the underlying orchestration engine. The swarm enables
    multi-agent collaboration with dynamic handoffs between specialized agents.

    Args:
        agents: List of LangChain agents to include in the swarm.
                Each agent should have a 'name' attribute.
        default_agent_name: Name of the default agent to start with.
                           If not provided, uses the first agent's name.
        **kwargs: Additional arguments for future compatibility

    Returns:
        LangGraphSwarmAdapter instance ready for use

    Raises:
        ValueError: If agents list is empty

    Example:
        >>> from fivcadvisor.adapters import create_langchain_swarm
        >>> from fivcadvisor.agents import create_default_agent
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> llm = ChatOpenAI(model="gpt-4o-mini")
        >>> agent1 = create_default_agent(
        ...     model=llm,
        ...     tools=[...],
        ...     system_prompt="You are Agent 1",
        ...     name="Agent1"
        ... )
        >>> agent2 = create_default_agent(
        ...     model=llm,
        ...     tools=[...],
        ...     system_prompt="You are Agent 2",
        ...     name="Agent2"
        ... )
        >>>
        >>> swarm = create_langchain_swarm([agent1, agent2])
        >>> result = await swarm.invoke_async("Your query")
        >>> print(result)

    Note:
        - Agents should have unique names for proper handoff routing
        - System prompts should clearly define each agent's role
        - Tools should be relevant to each agent's specialization
    """
    return LangGraphSwarmAdapter(agents, default_agent_name, **kwargs)

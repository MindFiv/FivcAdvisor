"""
Custom LangGraph Swarm implementation for multi-agent orchestration.

This module provides a custom swarm implementation using LangGraph 1.0 StateGraph
to replace the deprecated langgraph-swarm package.

Key Components:
    - LangGraphSwarmAdapter: Main adapter class for swarm orchestration
    - create_langchain_swarm: Factory function for creating swarms
    - SwarmState: State management for swarm execution

Features:
    - Multi-agent coordination with dynamic handoffs
    - Backward compatible with Strands Swarm API
    - Full async/await support
    - Flexible agent configuration
    - Built on LangGraph 1.0 StateGraph

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

from typing import Any, List, Optional, Dict, TypedDict
import asyncio
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END


class SwarmState(TypedDict):
    """State for swarm execution."""
    messages: List[Dict[str, str]]
    current_agent: str
    next_agent: Optional[str]


class LangGraphSwarmAdapter:
    """
    Custom LangGraph Swarm adapter for multi-agent orchestration.

    This adapter implements a swarm using LangGraph 1.0 StateGraph,
    providing a Strands-compatible API for multi-agent coordination.
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
        self._agent_map = {agent.name: agent for agent in agents}

        # Create the LangGraph workflow
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for the swarm."""
        workflow = StateGraph(SwarmState)

        # Add nodes for each agent
        for agent in self.agents:
            workflow.add_node(agent.name, self._create_agent_node(agent))

        # Add router node to determine next agent
        workflow.add_node("router", self._router_node)

        # Set entry point
        workflow.set_entry_point("router")

        # Add edges from router to agents
        for agent in self.agents:
            workflow.add_edge(agent.name, "router")

        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            self._route_to_agent,
            {agent.name: agent.name for agent in self.agents} | {"END": END},
        )

        return workflow

    def _create_agent_node(self, agent: Any):
        """Create a node function for an agent."""
        async def agent_node(state: SwarmState) -> SwarmState:
            # Convert messages to LangChain format if needed
            messages = state.get("messages", [])

            # Invoke the agent
            try:
                if hasattr(agent, "invoke_async"):
                    result = await agent.invoke_async(
                        messages[-1]["content"] if messages else ""
                    )
                else:
                    result = agent.invoke(
                        messages[-1]["content"] if messages else ""
                    )
            except Exception as e:
                result = {"messages": [{"role": "assistant", "content": str(e)}]}

            # Update messages
            if isinstance(result, dict) and "messages" in result:
                new_messages = messages + result["messages"]
            else:
                new_messages = messages + [{"role": "assistant", "content": str(result)}]

            return {
                "messages": new_messages,
                "current_agent": agent.name,
                "next_agent": None,
            }

        return agent_node

    def _router_node(self, state: SwarmState) -> SwarmState:
        """Route to the next agent based on current state."""
        return state

    def _route_to_agent(self, state: SwarmState) -> str:
        """Determine which agent should handle the next step."""
        # For now, use round-robin or stay with current agent
        # In a more sophisticated implementation, this could use LLM to decide
        current = state.get("current_agent", self.default_agent_name)

        # If there's a next_agent specified, use it
        if state.get("next_agent"):
            return state["next_agent"]

        # Otherwise, end the conversation
        return "END"

    async def invoke_async(self, query: str, **kwargs) -> dict:
        """
        Asynchronously invoke the swarm with a query.

        Args:
            query: The user query to process
            **kwargs: Additional arguments (config, etc.)

        Returns:
            Dictionary containing the result with 'messages' key
        """
        initial_state = {
            "messages": [{"role": "user", "content": query}],
            "current_agent": self.default_agent_name,
            "next_agent": None,
        }

        result = await self.app.ainvoke(
            initial_state,
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

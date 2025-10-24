"""
LangGraph Swarm adapter for multi-agent orchestration.

This module provides a wrapper around LangGraph Swarm to replace Strands Swarm
with minimal changes to existing code.
"""

from typing import Any, List, Optional
from langgraph_swarm import create_swarm


class LangGraphSwarmAdapter:
    """
    Adapter for LangGraph Swarm that provides a Strands-compatible API.
    
    This adapter wraps LangGraph Swarm to maintain compatibility with existing
    code that expects a Strands Swarm interface.
    """
    
    def __init__(
        self,
        agents: List[Any],
        default_agent_name: Optional[str] = None,
        **kwargs
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
            agents=agents,
            default_active_agent=self.default_agent_name
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
            config=kwargs.get("config")
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
        import asyncio
        return asyncio.run(self.invoke_async(query, **kwargs))


def create_langchain_swarm(
    agents: List[Any],
    default_agent_name: Optional[str] = None,
    **kwargs
) -> LangGraphSwarmAdapter:
    """
    Create a LangGraph Swarm adapter.
    
    This is the main factory function for creating a swarm of agents using
    LangGraph Swarm as the underlying orchestration engine.
    
    Args:
        agents: List of LangChain agents to include in the swarm
        default_agent_name: Name of the default agent to start with
        **kwargs: Additional arguments for future compatibility
        
    Returns:
        LangGraphSwarmAdapter instance
        
    Example:
        >>> from langchain.agents import create_react_agent
        >>> from langchain_openai import ChatOpenAI
        >>> 
        >>> model = ChatOpenAI(model="gpt-4")
        >>> agent1 = create_react_agent(model, tools=[...], name="Agent1")
        >>> agent2 = create_react_agent(model, tools=[...], name="Agent2")
        >>> 
        >>> swarm = create_langchain_swarm([agent1, agent2])
        >>> result = await swarm.invoke_async("Your query")
    """
    return LangGraphSwarmAdapter(agents, default_agent_name, **kwargs)


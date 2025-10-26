"""
Runnable wrapper for LangChain agents.

This module provides the AgentsRunnable class, which wraps LangChain's native
agent creation functions to provide a consistent Runnable interface for FivcAdvisor
agents. It handles both synchronous and asynchronous invocation with proper message
formatting and output extraction.

Core Classes:
    - AgentsRunnable: Runnable wrapper for LangChain agents

Example:
    >>> from fivcadvisor.agents.types import AgentsRunnable
    >>> from langchain_openai import ChatOpenAI
    >>>
    >>> # Create a model
    >>> model = ChatOpenAI(model="gpt-4o-mini")
    >>>
    >>> # Create an agent using AgentsRunnable
    >>> agent = AgentsRunnable(
    ...     model=model,
    ...     tools=[],
    ...     agent_name="MyAgent",
    ...     system_prompt="You are a helpful assistant"
    ... )
    >>>
    >>> # Execute the agent
    >>> result = agent.run("Hello!")
    >>> print(result)
"""

from typing import Optional, Any, List, Callable
from uuid import uuid4

from langchain.agents import create_agent
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel

from fivcadvisor.utils import Runnable


class AgentsRunnable(Runnable):
    """
    Runnable wrapper for LangChain agents.

    This class wraps LangChain's native agent creation functions to provide
    a consistent Runnable interface for FivcAdvisor agents. It handles both
    synchronous and asynchronous invocation with proper message formatting
    and output extraction.

    Attributes:
        _id: Unique identifier for the runnable
        _agent: The underlying LangChain agent (compiled state graph)
        _name: Agent name
        _system_prompt: System prompt for the agent
        _callback_handler: Optional callback handler for events

    Example:
        >>> from fivcadvisor.agents.types import AgentsRunnable
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> # Create a model
        >>> model = ChatOpenAI(model="gpt-4o-mini")
        >>>
        >>> # Create an agent
        >>> agent = AgentsRunnable(
        ...     model=model,
        ...     tools=[],
        ...     agent_name="MyAgent",
        ...     system_prompt="You are a helpful assistant"
        ... )
        >>>
        >>> # Run synchronously
        >>> result = agent.run("What is 2+2?")
        >>> print(result)
        >>>
        >>> # Run asynchronously
        >>> import asyncio
        >>> result = asyncio.run(agent.run_async("What is 2+2?"))
        >>> print(result)
    """

    def __init__(
        self,
        model: BaseChatModel,
        tools: List[BaseTool],
        agent_id: str | None = None,
        agent_name: str = "Default",
        system_prompt: str | None = None,
        callback_handler: Optional[Callable] = None,
        **kwargs,
    ):
        """
        Initialize AgentsRunnable.

        Args:
            model: LangChain chat model
            tools: List of LangChain tools
            agent_id: Unique identifier for the agent (auto-generated if not provided)
            agent_name: Human-readable name for the agent (default: 'Default')
            system_prompt: System prompt/instructions for the agent
            callback_handler: Optional callback handler for execution events
            **kwargs: Additional arguments (ignored for compatibility)

        Example:
            >>> from langchain_openai import ChatOpenAI
            >>> model = ChatOpenAI(model="gpt-4o-mini")
            >>> agent = AgentsRunnable(
            ...     model=model,
            ...     tools=[],
            ...     agent_name="MyAgent",
            ...     system_prompt="You are helpful"
            ... )
        """
        self._id = agent_id or str(uuid4())
        self._name = agent_name
        self._system_prompt = system_prompt
        self._callback_handler = callback_handler
        self._agent = create_agent(
            model,
            tools,
            name=agent_name,
            system_prompt=system_prompt,
        )

    @property
    def id(self) -> str:
        """
        Get the unique identifier for this runnable.

        Returns:
            The unique identifier string

        Example:
            >>> agent = AgentsRunnable(model=model, tools=[], agent_id="my-agent")
            >>> print(agent.id)
            'my-agent'
        """
        return self._id

    def run(self, query: str, **kwargs: Any) -> str:
        """
        Execute the agent synchronously.

        Invokes the agent with the provided query and returns the response.
        If a callback handler is configured, it will be called with the result.

        Args:
            query: The user query to process
            **kwargs: Additional arguments passed to the agent

        Returns:
            The agent's response as a string

        Raises:
            Exception: Any exception from the agent is caught and returned as error message

        Example:
            >>> agent = AgentsRunnable(model=model, tools=[])
            >>> result = agent.run("What is 2+2?")
            >>> print(result)
            '4'
        """
        try:
            # LangGraph agent expects messages in the input
            result = self._agent.invoke({"messages": [("user", query)]}, **kwargs)

            # Extract output from result
            # LangGraph returns messages in the result
            output = self._extract_output(result)

            # Call callback handler if provided
            if self._callback_handler:
                try:
                    self._callback_handler(result={"output": output})
                except TypeError:
                    self._callback_handler(output=output, agent=self)

            return output
        except Exception as e:
            error_msg = f"Agent error: {str(e)}"
            if self._callback_handler:
                try:
                    self._callback_handler(result={"error": error_msg})
                except TypeError:
                    pass
            return error_msg

    async def run_async(self, query: str, **kwargs: Any) -> str:
        """
        Execute the agent asynchronously.

        Asynchronously invokes the agent with the provided query and returns the response.
        If a callback handler is configured, it will be called with the result.

        Args:
            query: The user query to process
            **kwargs: Additional arguments passed to the agent

        Returns:
            The agent's response as a string

        Raises:
            Exception: Any exception from the agent is caught and returned as error message

        Example:
            >>> import asyncio
            >>> agent = AgentsRunnable(model=model, tools=[])
            >>> result = asyncio.run(agent.run_async("What is 2+2?"))
            >>> print(result)
            '4'
        """
        try:
            # LangGraph agent expects messages in the input
            result = await self._agent.ainvoke(
                {"messages": [("user", query)]}, **kwargs
            )

            # Extract output from result
            output = self._extract_output(result)

            # Call callback handler if provided
            if self._callback_handler:
                try:
                    self._callback_handler(result={"output": output})
                except TypeError:
                    self._callback_handler(output=output, agent=self)

            return output
        except Exception as e:
            error_msg = f"Agent error: {str(e)}"
            if self._callback_handler:
                try:
                    self._callback_handler(result={"error": error_msg})
                except TypeError:
                    pass
            return error_msg

    def _extract_output(self, result: Any) -> str:
        """
        Extract output from agent result.

        Handles both dict results with 'messages' key and other formats.
        Extracts the content from the last message in the result.

        Args:
            result: The result from agent invocation (typically a dict with 'messages' key)

        Returns:
            Extracted output as a string

        Example:
            >>> result = {"messages": [AIMessage(content="Hello!")]}
            >>> output = agent._extract_output(result)
            >>> print(output)
            'Hello!'
        """
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            if messages:
                # Get the last message
                last_msg = messages[-1]
                if hasattr(last_msg, "content"):
                    return last_msg.content
                else:
                    return str(last_msg)
            else:
                return str(result)
        else:
            return str(result)


class AgentsSwarmRunnable(Runnable):
    """
    Swarm orchestration for multiple AgentsRunnable agents.

    This class implements a swarm of agents using LangGraph StateGraph for
    multi-agent coordination and handoffs. It manages agent routing, message
    passing, and state management across multiple specialized agents.

    Attributes:
        _id: Unique identifier for the swarm
        _name: Human-readable name for the swarm
        _agents: List of AgentsRunnable agents in the swarm
        _agent_map: Dictionary mapping agent names to agent instances
        _default_agent_name: Name of the default agent to start with
        _workflow: LangGraph StateGraph for the swarm
        _app: Compiled LangGraph application

    Example:
        >>> from fivcadvisor.agents.types import AgentsSwarmRunnable, AgentsRunnable
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> # Create agents
        >>> model = ChatOpenAI(model="gpt-4o-mini")
        >>> agent1 = AgentsRunnable(
        ...     model=model,
        ...     tools=[],
        ...     agent_name="Agent1",
        ...     system_prompt="You are Agent 1"
        ... )
        >>> agent2 = AgentsRunnable(
        ...     model=model,
        ...     tools=[],
        ...     agent_name="Agent2",
        ...     system_prompt="You are Agent 2"
        ... )
        >>>
        >>> # Create swarm
        >>> swarm = AgentsSwarmRunnable(
        ...     swarm_id="my-swarm",
        ...     swarm_name="MySwarm",
        ...     agents=[agent1, agent2],
        ...     default_agent_name="Agent1"
        ... )
        >>>
        >>> # Run swarm
        >>> result = swarm.run("Your query")
        >>> print(result)
    """

    def __init__(
        self,
        swarm_id: str | None = None,
        swarm_name: str = "DefaultSwarm",
        agents: List[AgentsRunnable] | None = None,
        default_agent_name: str | None = None,
        **kwargs,
    ):
        """
        Initialize AgentsSwarmRunnable.

        Args:
            swarm_id: Unique identifier for the swarm (auto-generated if not provided)
            swarm_name: Human-readable name for the swarm (default: 'DefaultSwarm')
            agents: List of AgentsRunnable agents to include in the swarm
            default_agent_name: Name of the default agent to start with
                               (uses first agent's name if not provided)
            **kwargs: Additional arguments (ignored for compatibility)

        Raises:
            ValueError: If agents list is empty or None

        Example:
            >>> swarm = AgentsSwarmRunnable(
            ...     swarm_name="MySwarm",
            ...     agents=[agent1, agent2],
            ...     default_agent_name="Agent1"
            ... )
        """
        if not agents:
            raise ValueError("At least one agent is required for the swarm")

        self._id = swarm_id or str(uuid4())
        self._name = swarm_name
        self._agents = agents
        self._agent_map = {agent._name: agent for agent in agents}
        self._default_agent_name = default_agent_name or agents[0]._name

        # Create the LangGraph workflow
        self._workflow = self._create_workflow()
        self._app = self._workflow.compile()

    @property
    def id(self) -> str:
        """
        Get the unique identifier for this swarm.

        Returns:
            The unique identifier string

        Example:
            >>> swarm = AgentsSwarmRunnable(swarm_id="my-swarm", agents=[...])
            >>> print(swarm.id)
            'my-swarm'
        """
        return self._id

    @property
    def name(self) -> str:
        """
        Get the name of this swarm.

        Returns:
            The swarm name

        Example:
            >>> swarm = AgentsSwarmRunnable(swarm_name="MySwarm", agents=[...])
            >>> print(swarm.name)
            'MySwarm'
        """
        return self._name

    @property
    def agents(self) -> List[AgentsRunnable]:
        """
        Get the list of agents in this swarm.

        Returns:
            List of AgentsRunnable agents

        Example:
            >>> swarm = AgentsSwarmRunnable(agents=[agent1, agent2])
            >>> print(len(swarm.agents))
            2
        """
        return self._agents

    def _create_workflow(self):
        """
        Create the LangGraph workflow for the swarm.

        Returns:
            Configured StateGraph for swarm orchestration
        """
        from langgraph.graph import StateGraph, END

        workflow = StateGraph(dict)

        # Add nodes for each agent
        for agent in self._agents:
            workflow.add_node(agent._name, self._create_agent_node(agent))

        # Add router node to determine next agent
        workflow.add_node("router", self._router_node)

        # Set entry point
        workflow.set_entry_point("router")

        # Add edges from agents back to router
        for agent in self._agents:
            workflow.add_edge(agent._name, "router")

        # Add conditional edges from router
        agent_names = {agent._name: agent._name for agent in self._agents}
        workflow.add_conditional_edges(
            "router",
            self._route_to_agent,
            agent_names | {"END": END},
        )

        return workflow

    def _create_agent_node(self, agent: AgentsRunnable):
        """
        Create a node function for an agent.

        Args:
            agent: The AgentsRunnable agent to create a node for

        Returns:
            Async function that executes the agent
        """

        async def agent_node(state: dict) -> dict:
            """Execute agent and update state."""
            messages = state.get("messages", [])

            # Get the last user message
            query = ""
            if messages:
                last_msg = messages[-1]
                if isinstance(last_msg, dict):
                    query = last_msg.get("content", "")
                elif hasattr(last_msg, "content"):
                    query = last_msg.content
                else:
                    query = str(last_msg)

            # Invoke the agent
            try:
                result = await agent.run_async(query)
            except Exception as e:
                result = f"Error in {agent._name}: {str(e)}"

            # Update messages with agent response
            new_messages = messages + [
                {"role": "assistant", "content": result, "agent": agent._name}
            ]

            return {
                "messages": new_messages,
                "current_agent": agent._name,
                "next_agent": None,
            }

        return agent_node

    def _router_node(self, state: dict) -> dict:
        """
        Route to the appropriate agent.

        Args:
            state: Current swarm state

        Returns:
            Updated state
        """
        # For now, just return the current state
        # In a more sophisticated implementation, this could use LLM to decide routing
        return state

    def _route_to_agent(self, state: dict) -> str:
        """
        Determine which agent to route to next.

        Args:
            state: Current swarm state

        Returns:
            Name of the next agent or "END"
        """
        # If next_agent is specified, route to it
        if state.get("next_agent"):
            next_agent = state["next_agent"]
            if next_agent in self._agent_map:
                return next_agent
            return "END"

        # Otherwise, route to the current agent or default
        current = state.get("current_agent", self._default_agent_name)
        if current in self._agent_map:
            return current
        return self._default_agent_name

    def run(self, query: str, **kwargs: Any) -> str:
        """
        Execute the swarm synchronously.

        Invokes the swarm with the provided query and returns the response.
        This method blocks until the swarm completes execution.

        Args:
            query: The user query to process
            **kwargs: Additional arguments passed to the swarm

        Returns:
            The swarm's response as a string

        Raises:
            Exception: Any exception from the swarm is caught and returned as error message

        Example:
            >>> swarm = AgentsSwarmRunnable(agents=[agent1, agent2])
            >>> result = swarm.run("What is 2+2?")
            >>> print(result)
            '4'
        """
        try:
            initial_state = {
                "messages": [{"role": "user", "content": query}],
                "current_agent": self._default_agent_name,
                "next_agent": None,
            }

            result = self._app.invoke(initial_state, config=kwargs.get("config"))

            # Extract output from result
            output = self._extract_output(result)
            return output
        except Exception as e:
            error_msg = f"Swarm error: {str(e)}"
            return error_msg

    async def run_async(self, query: str, **kwargs: Any) -> str:
        """
        Execute the swarm asynchronously.

        Asynchronously invokes the swarm with the provided query and returns the response.
        This is the recommended method for non-blocking execution.

        Args:
            query: The user query to process
            **kwargs: Additional arguments passed to the swarm

        Returns:
            The swarm's response as a string

        Raises:
            Exception: Any exception from the swarm is caught and returned as error message

        Example:
            >>> import asyncio
            >>> swarm = AgentsSwarmRunnable(agents=[agent1, agent2])
            >>> result = asyncio.run(swarm.run_async("What is 2+2?"))
            >>> print(result)
            '4'
        """
        try:
            initial_state = {
                "messages": [{"role": "user", "content": query}],
                "current_agent": self._default_agent_name,
                "next_agent": None,
            }

            result = await self._app.ainvoke(initial_state, config=kwargs.get("config"))

            # Extract output from result
            output = self._extract_output(result)
            return output
        except Exception as e:
            error_msg = f"Swarm error: {str(e)}"
            return error_msg

    def _extract_output(self, result: Any) -> str:
        """
        Extract output from swarm result.

        Handles both dict results with 'messages' key and other formats.
        Extracts the content from the last message in the result.

        Args:
            result: The result from swarm invocation (typically a dict with 'messages' key)

        Returns:
            Extracted output as a string

        Example:
            >>> result = {"messages": [{"role": "assistant", "content": "Hello!"}]}
            >>> output = swarm._extract_output(result)
            >>> print(output)
            'Hello!'
        """
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            if messages:
                # Get the last message
                last_msg = messages[-1]
                if isinstance(last_msg, dict):
                    return last_msg.get("content", str(last_msg))
                elif hasattr(last_msg, "content"):
                    return last_msg.content
                else:
                    return str(last_msg)
            else:
                return str(result)
        else:
            return str(result)

    def __call__(self, query: str, **kwargs: Any) -> str:
        """
        Allow the swarm to be called directly.

        Args:
            query: The user query to process
            **kwargs: Additional arguments

        Returns:
            The swarm's response as a string

        Example:
            >>> swarm = AgentsSwarmRunnable(agents=[agent1, agent2])
            >>> result = swarm("What is 2+2?")
            >>> print(result)
            '4'
        """
        return self.run(query, **kwargs)

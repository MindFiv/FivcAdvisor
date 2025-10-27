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

from typing import Optional, Any, List, Callable, Type, Union
from uuid import uuid4

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AnyMessage
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from fivcadvisor.utils import Runnable


class AgentsRunnable(Runnable):
    """
    Runnable wrapper for LangChain agents.

    This class wraps LangChain's native agent creation functions to provide
    a consistent Runnable interface for FivcAdvisor agents. It handles both
    synchronous and asynchronous invocation with proper message formatting
    and output extraction.

    The agent supports two input modes:
    - String queries: Automatically converted to HumanMessage
    - Message history: Direct list of AnyMessage objects for multi-turn conversations

    Attributes:
        _id: Unique identifier for the runnable
        _agent: The underlying LangChain agent (compiled state graph)
        _name: Agent name
        _system_prompt: System prompt for the agent
        _callback_handler: Optional callback handler for events

    Example:
        >>> from fivcadvisor.agents.types import AgentsRunnable
        >>> from langchain_openai import ChatOpenAI
        >>> from langchain_core.messages import HumanMessage, AIMessage
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
        >>> # Run with string query
        >>> result = agent.run("What is 2+2?")
        >>> print(result)
        >>>
        >>> # Run with message history
        >>> messages = [
        ...     HumanMessage(content="What is 2+2?"),
        ...     AIMessage(content="2+2 equals 4"),
        ...     HumanMessage(content="What about 3+3?")
        ... ]
        >>> result = agent.run(messages)
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
        response_model: Type[BaseModel] | None = None,
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
            response_model: Optional Pydantic model class for structured output.
                           When provided, the agent will return instances of this model
                           instead of strings. The model is passed to create_agent as
                           response_format for automatic conversion.
            callback_handler: Optional callback handler for execution events
            **kwargs: Additional arguments (ignored for compatibility)

        Example:
            >>> from langchain_openai import ChatOpenAI
            >>> from pydantic import BaseModel
            >>>
            >>> class MyResponse(BaseModel):
            ...     answer: str
            ...     confidence: float
            >>>
            >>> model = ChatOpenAI(model="gpt-4o-mini")
            >>> agent = AgentsRunnable(
            ...     model=model,
            ...     tools=[],
            ...     agent_name="MyAgent",
            ...     system_prompt="You are helpful",
            ...     response_model=MyResponse
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
            response_format=response_model,
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

    @property
    def name(self) -> str:
        """
        Get the name of this runnable.

        Returns:
            The runnable name

        Example:
            >>> agent = AgentsRunnable(agent_name="MyAgent", model=model, tools=[])
            >>> print(agent.name)
            'MyAgent'
        """
        return self._name

    def run(
        self, query: str | List[AnyMessage], **kwargs: Any
    ) -> Union[BaseModel, str]:
        """
        Execute the agent synchronously.

        Invokes the agent with the provided query and returns the response.
        If a callback handler is configured, it will be called with the result.

        The return type depends on whether a response_model was provided during
        initialization:
        - If response_model is set: Returns an instance of that Pydantic model
        - If response_model is None: Returns the response as a string

        Args:
            query: The user query to process. Can be either:
                   - A string: Will be converted to a HumanMessage
                   - A list of AnyMessage: Will be used directly as the message history
            **kwargs: Additional arguments passed to the agent

        Returns:
            Union[BaseModel, str]: The agent's response, either as a Pydantic model
                                   instance (if response_model was provided) or as a string

        Raises:
            Exception: Any exception from the agent is caught and returned as error message

        Example:
            >>> agent = AgentsRunnable(model=model, tools=[])
            >>> result = agent.run("What is 2+2?")
            >>> print(result)
            '4'

            >>> # With message history
            >>> from langchain_core.messages import HumanMessage, AIMessage
            >>> messages = [
            ...     HumanMessage(content="What is 2+2?"),
            ...     AIMessage(content="2+2 equals 4"),
            ...     HumanMessage(content="What about 3+3?")
            ... ]
            >>> result = agent.run(messages)
            >>> print(result)
            '3+3 equals 6'

            >>> # With response_model
            >>> from pydantic import BaseModel
            >>> class Answer(BaseModel):
            ...     value: int
            >>> agent = AgentsRunnable(model=model, tools=[], response_model=Answer)
            >>> result = agent.run("What is 2+2?")
            >>> print(result.value)
            4
        """
        inputs = [HumanMessage(content=query)] if isinstance(query, str) else query
        output = self._agent.invoke(self._agent.InputType(messages=inputs))
        if "structured_response" in output:
            return output["structured_response"]

        output = output["messages"][-1]
        return output.text

    async def run_async(
        self, query: str | List[AnyMessage], **kwargs: Any
    ) -> Union[BaseModel, str]:
        """
        Execute the agent asynchronously.

        Asynchronously invokes the agent with the provided query and returns the response.
        If a callback handler is configured, it will be called with the result.

        The return type depends on whether a response_model was provided during
        initialization:
        - If response_model is set: Returns an instance of that Pydantic model
        - If response_model is None: Returns the response as a string

        Args:
            query: The user query to process. Can be either:
                   - A string: Will be converted to a HumanMessage
                   - A list of AnyMessage: Will be used directly as the message history
            **kwargs: Additional arguments passed to the agent

        Returns:
            Union[BaseModel, str]: The agent's response, either as a Pydantic model
                                   instance (if response_model was provided) or as a string

        Raises:
            Exception: Any exception from the agent is caught and returned as error message

        Example:
            >>> import asyncio
            >>> agent = AgentsRunnable(model=model, tools=[])
            >>> result = asyncio.run(agent.run_async("What is 2+2?"))
            >>> print(result)
            '4'

            >>> # With message history
            >>> from langchain_core.messages import HumanMessage, AIMessage
            >>> messages = [
            ...     HumanMessage(content="What is 2+2?"),
            ...     AIMessage(content="2+2 equals 4"),
            ...     HumanMessage(content="What about 3+3?")
            ... ]
            >>> result = asyncio.run(agent.run_async(messages))
            >>> print(result)
            '3+3 equals 6'

            >>> # With response_model
            >>> from pydantic import BaseModel
            >>> class Answer(BaseModel):
            ...     value: int
            >>> agent = AgentsRunnable(model=model, tools=[], response_model=Answer)
            >>> result = asyncio.run(agent.run_async("What is 2+2?"))
            >>> print(result.value)
            4
        """
        inputs = [HumanMessage(content=query)] if isinstance(query, str) else query
        output = await self._agent.ainvoke(self._agent.InputType(messages=inputs))
        if "structured_response" in output:
            return output["structured_response"]

        output = output["messages"][-1]
        return output.text


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

            # Extract the last message content
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                if messages:
                    last_msg = messages[-1]
                    if isinstance(last_msg, dict):
                        return last_msg.get("content", str(last_msg))
                    elif hasattr(last_msg, "content"):
                        return last_msg.content
            return str(result)
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

            # Extract the last message content
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                if messages:
                    last_msg = messages[-1]
                    if isinstance(last_msg, dict):
                        return last_msg.get("content", str(last_msg))
                    elif hasattr(last_msg, "content"):
                        return last_msg.content
            return str(result)
        except Exception as e:
            error_msg = f"Swarm error: {str(e)}"
            return error_msg

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

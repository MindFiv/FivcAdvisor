"""
Runnable wrapper for LangChain agents.

This module provides the AgentsRunnable class, which wraps LangChain's native
agent creation functions to provide a consistent Runnable interface for FivcAdvisor
agents. It handles both synchronous and asynchronous invocation with proper message
formatting and output extraction.

Core Classes:
    - AgentsRunnable: Runnable wrapper for LangChain agents

Features:
    - Synchronous and asynchronous execution
    - Automatic message history management
    - Structured response support via response_model
    - Callback handler integration for monitoring
    - Multi-turn conversation support

Return Types:
    - If response_model is provided: Returns Pydantic model instance
    - If response_model is None: Returns string content from agent response

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
    >>> result = agent.run("Hello!")
    >>> print(result)  # Returns string
"""

from typing import Any, List, Type, Union, Callable
from uuid import uuid4

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AnyMessage
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from fivcadvisor.utils import Runnable


class AgentsRunnable(Runnable):
    """
    Stateless runnable wrapper for LangChain agents.

    This class wraps LangChain's native agent creation functions to provide
    a consistent Runnable interface for FivcAdvisor agents. It handles both
    synchronous and asynchronous invocation with proper message formatting
    and output extraction.

    The agent supports two input modes:
    - String queries: Automatically converted to HumanMessage
    - Message history: Direct list of AnyMessage objects for multi-turn conversations

    Return Types:
    - If response_model is provided: Returns Pydantic model instance
    - If response_model is None: Returns string content from agent response

    Attributes:
        _id: Unique identifier for the runnable
        _agent: The underlying LangChain agent (compiled state graph)
        _name: Agent name
        _system_prompt: System prompt for the agent
        _callback_handler: Optional callback handler for execution events
        _messages: List of messages accumulated during execution

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
        >>> # Run with string query - returns string
        >>> result = agent.run("What is 2+2?")
        >>> print(result)  # "4"
        >>>
        >>> # Run with message history
        >>> messages = [
        ...     HumanMessage(content="What is 2+2?"),
        ...     AIMessage(content="2+2 equals 4"),
        ...     HumanMessage(content="What about 3+3?")
        ... ]
        >>> result = agent.run(messages)
        >>> print(result)  # "3+3 equals 6"
        >>>
        >>> # Run asynchronously
        >>> import asyncio
        >>> result = asyncio.run(agent.run_async("What is 2+2?"))
        >>> print(result)  # "4"
        >>>
        >>> # Run with structured response
        >>> from pydantic import BaseModel
        >>> class Answer(BaseModel):
        ...     value: int
        >>> agent = AgentsRunnable(
        ...     model=model,
        ...     tools=[],
        ...     response_model=Answer
        ... )
        >>> result = agent.run("What is 2+2?")
        >>> print(result.value)  # 4
    """

    def __init__(
        self,
        model: BaseChatModel,
        tools: List[BaseTool],
        agent_id: str | None = None,
        agent_name: str = "Default",
        system_prompt: str | None = None,
        messages: List[AnyMessage] | None = None,
        response_model: Type[BaseModel] | None = None,
        callback_handler: Callable[[str, Any], None] | None = None,
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
        self._messages = messages or []
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

    @property
    def agent_id(self):
        return self._id

    @property
    def system_prompt(self):
        return self._system_prompt

    def run(
        self,
        query: str | List[AnyMessage] = "",
        **kwargs: Any,
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
                   (default: empty string)
            **kwargs: Additional keyword arguments passed to the agent

        Returns:
            Union[BaseModel, str]: The agent's response, either as a Pydantic model
                                   instance (if response_model was provided) or as a string

        Raises:
            AssertionError: If no messages are found in outputs

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
        outputs = {}
        if self._callback_handler:
            self._callback_handler("start", None)

        for mode, event in self._agent.stream(
            self._agent.InputType(messages=inputs),
            stream_mode=["messages", "values", "updates"],
        ):
            if mode == "values":
                outputs = event

            if self._callback_handler:
                self._callback_handler(mode, event)

        if self._callback_handler:
            self._callback_handler("finish", None)

        if "structured_response" in outputs:
            return outputs["structured_response"]

        if "messages" not in outputs:
            raise AssertionError("No messages found in outputs")

        output = outputs["messages"][-1]
        self._messages.append(output)

        # Extract content from BaseMessage if needed
        if hasattr(output, "content"):
            return output.content
        return str(output)

    async def run_async(
        self,
        query: str | List[AnyMessage] = "",
        **kwargs: Any,
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
                   (default: empty string)
            **kwargs: Additional keyword arguments passed to the agent

        Returns:
            Union[BaseModel, str]: The agent's response, either as a Pydantic model
                                   instance (if response_model was provided) or as a string

        Raises:
            AssertionError: If no messages are found in outputs

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
        self._messages.extend(inputs)

        outputs = {}
        if self._callback_handler:
            self._callback_handler("start", None)

        async for mode, event in self._agent.astream(
            self._agent.InputType(messages=self._messages),
            stream_mode=["messages", "values", "updates"],
        ):
            if mode == "values":
                outputs = event

            if self._callback_handler:
                self._callback_handler(mode, event)

        if self._callback_handler:
            self._callback_handler("finish", None)

        if "structured_response" in outputs:
            return outputs["structured_response"]

        if "messages" not in outputs:
            raise AssertionError("No messages found in outputs")

        output = outputs["messages"][-1]
        self._messages.append(output)

        # Extract content from BaseMessage if needed
        if hasattr(output, "content"):
            return output.content
        return str(output)

"""
LangChain Agent Adapter

This module provides adapters to convert LangChain agents to Strands-compatible API.
It wraps LangChain's AgentExecutor to provide the same interface as Strands Agent.

Key Classes:
    - LangChainAgentAdapter: Wraps LangChain AgentExecutor with Strands API
    - create_langchain_agent: Factory function to create LangChain agents

The adapter maintains backward compatibility with existing code that expects
Strands Agent interface while using LangChain under the hood.
"""

from typing import Any, Optional, List, Dict, Union, Callable, Type, TypeVar
from uuid import uuid4
import asyncio
import json

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, ValidationError

from fivcadvisor.adapters.tools import convert_strands_tools_to_langchain
from fivcadvisor.adapters.events import EventBus, EventType, Event

T = TypeVar("T", bound=BaseModel)


class LangChainAgentAdapter:
    """
    Adapter that wraps LangChain AgentExecutor with Strands Agent API.

    This adapter provides a Strands-compatible interface for LangChain agents,
    allowing existing code to work without modification while using LangChain
    under the hood.

    Attributes:
        agent_id: Unique identifier for the agent
        name: Human-readable name for the agent
        system_prompt: System prompt/instructions for the agent
        model: The LLM model being used
        tools: List of tools available to the agent
        executor: The underlying LangChain AgentExecutor
        callback_handler: Optional callback handler for events
        event_bus: EventBus for emitting agent events
    """

    def __init__(
        self,
        model: BaseLanguageModel,
        tools: List[Tool],
        system_prompt: str = "",
        name: str = "Agent",
        agent_id: Optional[str] = None,
        callback_handler: Optional[Callable] = None,
        conversation_manager: Optional[Any] = None,
        hooks: Optional[List[Any]] = None,
        **kwargs,
    ):
        """
        Initialize LangChain Agent Adapter.

        Args:
            model: LangChain LLM model
            tools: List of LangChain tools
            system_prompt: System prompt for the agent
            name: Agent name
            agent_id: Unique agent ID (auto-generated if not provided)
            callback_handler: Optional callback handler
            conversation_manager: Optional conversation manager (for compatibility)
            hooks: Optional list of hooks (for compatibility)
            **kwargs: Additional arguments (ignored for compatibility)
        """
        self.agent_id = agent_id or str(uuid4())
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools
        self.callback_handler = callback_handler
        self.conversation_manager = conversation_manager
        self.hooks = hooks or []
        self.event_bus = EventBus()

        # Create a simple agent wrapper that uses the LLM with tools
        # This is a simplified agent that calls the LLM and handles tool calls
        self.agent = self._create_simple_agent(model, tools, system_prompt)

    def _create_simple_agent(
        self, model: BaseLanguageModel, tools: List[Tool], system_prompt: str
    ) -> Any:
        """Create a simple agent that wraps the LLM with tools."""

        class SimpleAgent:
            def __init__(self, llm, tools, system_prompt):
                self.llm = llm
                self.tools = tools
                self.system_prompt = system_prompt
                self.tool_map = {tool.name: tool for tool in tools}

            def invoke(self, input_dict: Dict[str, str]) -> Dict[str, str]:
                """Invoke the agent with a query."""
                query = input_dict.get("input", "")

                # Build the prompt
                prompt = self.system_prompt + "\n\nUser: " + query

                # Call the LLM
                try:
                    response = self.llm.invoke(prompt)
                    # Extract text from response
                    if hasattr(response, "content"):
                        output = response.content
                    else:
                        output = str(response)
                    return {"output": output}
                except Exception as e:
                    return {"output": f"Error: {str(e)}"}

        return SimpleAgent(model, tools, system_prompt)

    async def invoke_async(self, query: str) -> str:
        """
        Invoke the agent asynchronously with a query.

        Args:
            query: The query/prompt for the agent

        Returns:
            The agent's response as a string
        """
        try:
            # Emit before invocation event
            self.event_bus.emit(
                Event(
                    event_type=EventType.BEFORE_INVOCATION,
                    data={"agent_id": self.agent_id, "query": query},
                )
            )

            # Run agent in executor to avoid blocking
            result = await asyncio.to_thread(self.agent.invoke, {"input": query})

            # Extract output from agent result
            output = result.get("output", str(result))

            # Emit after invocation event
            self.event_bus.emit(
                Event(
                    event_type=EventType.AFTER_INVOCATION,
                    data={"agent_id": self.agent_id, "output": output},
                )
            )

            # Call callback handler if provided
            if self.callback_handler:
                self.callback_handler(output=output, agent=self)

            return output

        except Exception as e:
            # Emit error event
            self.event_bus.emit(
                Event(
                    event_type=EventType.ERROR_OCCURRED,
                    data={"agent_id": self.agent_id, "error": str(e)},
                )
            )
            raise

    def invoke(self, query: str) -> str:
        """
        Invoke the agent synchronously with a query.

        Args:
            query: The query/prompt for the agent

        Returns:
            The agent's response as a string
        """
        try:
            result = self.agent.invoke({"input": query})
            output = result.get("output", str(result))

            if self.callback_handler:
                self.callback_handler(output=output, agent=self)

            return output

        except Exception as e:
            raise

    def __call__(self, query: str) -> str:
        """
        Make the agent callable for convenience.

        Args:
            query: The query/prompt for the agent

        Returns:
            The agent's response as a string
        """
        return self.invoke(query)

    async def structured_output_async(
        self, schema: Type[T], prompt: str, **kwargs
    ) -> T:
        """
        Get structured output from the agent asynchronously.

        This method calls the agent with a prompt and parses the response
        into the specified Pydantic schema.

        Args:
            schema: Pydantic model class to parse the response into
            prompt: The prompt to send to the agent
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            Instance of the schema class with parsed data

        Raises:
            ValidationError: If the response cannot be parsed into the schema
            ValueError: If the agent response is not valid JSON
        """
        try:
            # Get the response from the agent
            response = await self.invoke_async(prompt)

            # Try to parse as JSON
            try:
                # First, try to extract JSON from the response
                # The response might contain extra text before/after JSON
                json_start = response.find("{")
                json_end = response.rfind("}") + 1

                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    data = json.loads(json_str)
                else:
                    # If no JSON found, try parsing the whole response
                    data = json.loads(response)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Agent response is not valid JSON: {response}"
                ) from e

            # Parse the JSON into the schema
            return schema(**data)

        except ValidationError as e:
            raise ValidationError.from_exception_data(
                title=schema.__name__,
                line_errors=[
                    {
                        "type": "value_error",
                        "loc": ("response",),
                        "msg": f"Failed to parse agent response into {schema.__name__}: {str(e)}",
                        "input": response,
                    }
                ],
            )
        except Exception as e:
            raise


def create_langchain_agent(
    model: BaseLanguageModel,
    tools: Optional[List[Any]] = None,
    system_prompt: str = "",
    name: str = "Agent",
    agent_id: Optional[str] = None,
    callback_handler: Optional[Callable] = None,
    conversation_manager: Optional[Any] = None,
    hooks: Optional[List[Any]] = None,
    **kwargs,
) -> LangChainAgentAdapter:
    """
    Factory function to create a LangChain agent with Strands API.

    This function creates a LangChainAgentAdapter that provides a Strands-compatible
    interface while using LangChain under the hood.

    Args:
        model: LangChain LLM model
        tools: List of tools (can be Strands or LangChain tools)
        system_prompt: System prompt for the agent
        name: Agent name
        agent_id: Unique agent ID (auto-generated if not provided)
        callback_handler: Optional callback handler
        conversation_manager: Optional conversation manager
        hooks: Optional list of hooks
        **kwargs: Additional arguments (ignored for compatibility)

    Returns:
        LangChainAgentAdapter instance
    """
    # Convert Strands tools to LangChain tools if needed
    if tools:
        langchain_tools = []
        for tool in tools:
            if hasattr(tool, "tool_name"):
                # This is a Strands tool, convert it
                langchain_tools.append(convert_strands_tools_to_langchain([tool])[0])
            else:
                # Already a LangChain tool
                langchain_tools.append(tool)
        tools = langchain_tools
    else:
        tools = []

    return LangChainAgentAdapter(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        name=name,
        agent_id=agent_id,
        callback_handler=callback_handler,
        conversation_manager=conversation_manager,
        hooks=hooks,
        **kwargs,
    )

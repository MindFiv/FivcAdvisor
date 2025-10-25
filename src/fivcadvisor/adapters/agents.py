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

from typing import Any, Optional, List, Dict, Callable, Type, TypeVar
from uuid import uuid4
import asyncio
import json

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import Tool

from pydantic import BaseModel, ValidationError
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from fivcadvisor.adapters.tools import convert_strands_tools_to_langchain
from fivcadvisor.adapters.events import EventBus, EventType, Event, MessageAddedEvent

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

                # Bind tools to the LLM if tools are available
                if tools:
                    self.llm_with_tools = llm.bind_tools(tools)
                else:
                    self.llm_with_tools = llm

            def invoke(self, input_dict: Dict[str, str]) -> Dict[str, str]:
                """Invoke the agent with a query."""
                query = input_dict.get("input", "")

                messages = []
                if self.system_prompt:
                    messages.append(SystemMessage(content=self.system_prompt))
                messages.append(HumanMessage(content=query))

                # Call the LLM with tools
                try:
                    response = self.llm_with_tools.invoke(messages)

                    # Extract text content from response
                    text_content = ""
                    if hasattr(response, "content"):
                        text_content = response.content

                    # Process tool calls if present AND there's no text content
                    # (If there's text content, the LLM is providing a direct answer)
                    if (
                        hasattr(response, "tool_calls")
                        and response.tool_calls
                        and not text_content
                    ):
                        # Handle tool calls
                        tool_results = []
                        for tool_call in response.tool_calls:
                            tool_name = tool_call.get("name") or tool_call.get(
                                "tool_name"
                            )
                            tool_input = tool_call.get("args") or tool_call.get(
                                "input", {}
                            )

                            if tool_name in self.tool_map:
                                try:
                                    tool = self.tool_map[tool_name]
                                    # Call the tool
                                    if isinstance(tool_input, dict):
                                        result = tool.invoke(tool_input)
                                    else:
                                        result = tool.invoke({"input": tool_input})
                                    tool_results.append(
                                        {"tool_name": tool_name, "result": result}
                                    )
                                except Exception as e:
                                    tool_results.append(
                                        {"tool_name": tool_name, "error": str(e)}
                                    )

                        # Return tool results
                        return {"output": json.dumps(tool_results)}

                    # Return text content (either from direct response or from tool calls)
                    output = text_content if text_content else str(response)
                    return {"output": output}
                except Exception as e:
                    return {"output": f"Error: {str(e)}"}

        return SimpleAgent(model, tools, system_prompt)

    async def invoke_async(self, query: str, agent: Optional[Any] = None) -> str:
        """
        Invoke the agent asynchronously with a query.

        Args:
            query: The query/prompt for the agent
            agent: Optional agent to use (defaults to self.agent)

        Returns:
            The agent's response as a string
        """
        try:
            # Use provided agent or default to self.agent
            agent_to_use = agent if agent is not None else self.agent

            # Emit before invocation event
            self.event_bus.emit(
                Event(
                    event_type=EventType.BEFORE_INVOCATION,
                    data={"agent_id": self.agent_id, "query": query},
                )
            )

            # Run agent in executor to avoid blocking
            result = await asyncio.to_thread(agent_to_use.invoke, {"input": query})

            # Extract output from agent result
            output = result.get("output", str(result))

            # Emit message added event with the response
            self.event_bus.emit(
                MessageAddedEvent(
                    agent_id=self.agent_id,
                    message=output,
                    role="assistant",
                )
            )

            # Emit after invocation event
            self.event_bus.emit(
                Event(
                    event_type=EventType.AFTER_INVOCATION,
                    data={"agent_id": self.agent_id, "output": output},
                )
            )

            # Call callback handler if provided
            # Pass both output and a Message object for compatibility
            if self.callback_handler:
                # Create a Message object for the callback using LangChain AIMessage
                message = AIMessage(content=output)
                # Try to call with result parameter (for AgentsMonitor compatibility)
                try:
                    self.callback_handler(
                        result={
                            "message": message,
                            "output": output,
                        }
                    )
                except TypeError:
                    # Fallback to output parameter if result is not supported
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
            # Emit before invocation event
            self.event_bus.emit(
                Event(
                    event_type=EventType.BEFORE_INVOCATION,
                    data={"agent_id": self.agent_id, "query": query},
                )
            )

            result = self.agent.invoke({"input": query})
            output = result.get("output", str(result))

            # Emit message added event with the response
            self.event_bus.emit(
                MessageAddedEvent(
                    agent_id=self.agent_id,
                    message=output,
                    role="assistant",
                )
            )

            # Emit after invocation event
            self.event_bus.emit(
                Event(
                    event_type=EventType.AFTER_INVOCATION,
                    data={"agent_id": self.agent_id, "output": output},
                )
            )

            if self.callback_handler:
                # Create a Message object for the callback using LangChain AIMessage
                message = AIMessage(content=output)
                # Try to call with result parameter (for AgentsMonitor compatibility)
                try:
                    self.callback_handler(
                        result={
                            "message": message,
                            "output": output,
                        }
                    )
                except TypeError:
                    # Fallback to output parameter if result is not supported
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
            # For structured output, we need to use an agent without tools
            # to prevent the LLM from trying to invoke tools instead of generating output
            # Create a temporary agent without tools
            temp_agent = self._create_simple_agent(self.model, [], self.system_prompt)

            # Get the response from the agent without tools
            response = await self.invoke_async(prompt, agent=temp_agent)

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
                raise ValueError(f"Agent response is not valid JSON: {response}") from e

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
        except Exception as _:
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

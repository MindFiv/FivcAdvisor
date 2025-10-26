"""
LangChain Agent wrapper using native LangChain functions.

This module provides a wrapper around LangChain's native agent creation functions
(langchain.agents.create_agent) to provide a consistent interface for FivcAdvisor agents.

Key Components:
    - LangChainAgent: Wrapper class for LangChain agents
    - create_langchain_agent: Factory function using native LangChain functions
"""

from typing import Any, Optional, List, Callable
from uuid import uuid4

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langchain.agents import create_agent


class LangChainAgent:
    """
    Wrapper for LangChain agents using native agent creation functions.

    This class wraps LangChain's AgentExecutor to provide a consistent interface
    for FivcAdvisor agents while using LangChain's native agent creation functions.
    """

    def __init__(
        self,
        model: BaseLanguageModel,
        tools: List[BaseTool],
        system_prompt: str = "",
        name: str = "Agent",
        agent_id: Optional[str] = None,
        callback_handler: Optional[Callable] = None,
        **kwargs,
    ):
        """
        Initialize LangChain Agent wrapper.

        Args:
            model: LangChain LLM model
            tools: List of LangChain tools
            system_prompt: System prompt for the agent
            name: Agent name
            agent_id: Unique agent ID (auto-generated if not provided)
            callback_handler: Optional callback handler
            **kwargs: Additional arguments (for compatibility)
        """
        self.agent_id = agent_id or str(uuid4())
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools
        self.callback_handler = callback_handler

        # Create the agent using LangChain's native tool-calling agent
        self.agent_executor = self._create_agent_executor(model, tools, system_prompt)

    def _create_agent_executor(
        self, model: BaseLanguageModel, tools: List[BaseTool], system_prompt: str
    ):
        """Create an agent using LangChain's native functions."""

        # Use LangChain's native create_agent function
        # This returns a compiled state graph that can be invoked
        agent = create_agent(
            model,
            tools=tools,
            system_prompt=system_prompt or "You are a helpful assistant.",
        )

        return agent

    def invoke(self, query: str, **kwargs) -> str:
        """
        Synchronously invoke the agent with a query.

        Args:
            query: The user query to process
            **kwargs: Additional arguments

        Returns:
            The agent's response as a string
        """
        try:
            # LangGraph agent expects messages in the input
            result = self.agent_executor.invoke(
                {"messages": [("user", query)]}, **kwargs
            )

            # Extract output from result
            # LangGraph returns messages in the result
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                if messages:
                    # Get the last message
                    last_msg = messages[-1]
                    if hasattr(last_msg, "content"):
                        output = last_msg.content
                    else:
                        output = str(last_msg)
                else:
                    output = str(result)
            else:
                output = str(result)

            # Call callback handler if provided
            if self.callback_handler:
                try:
                    self.callback_handler(result={"output": output})
                except TypeError:
                    self.callback_handler(output=output, agent=self)

            return output
        except Exception as e:
            error_msg = f"Agent error: {str(e)}"
            if self.callback_handler:
                try:
                    self.callback_handler(result={"error": error_msg})
                except TypeError:
                    pass
            return error_msg

    async def invoke_async(self, query: str, **kwargs) -> str:
        """
        Asynchronously invoke the agent with a query.

        Args:
            query: The user query to process
            **kwargs: Additional arguments

        Returns:
            The agent's response as a string
        """
        try:
            # LangGraph agent expects messages in the input
            result = await self.agent_executor.ainvoke(
                {"messages": [("user", query)]}, **kwargs
            )

            # Extract output from result
            # LangGraph returns messages in the result
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                if messages:
                    # Get the last message
                    last_msg = messages[-1]
                    if hasattr(last_msg, "content"):
                        output = last_msg.content
                    else:
                        output = str(last_msg)
                else:
                    output = str(result)
            else:
                output = str(result)

            # Call callback handler if provided
            if self.callback_handler:
                try:
                    self.callback_handler(result={"output": output})
                except TypeError:
                    self.callback_handler(output=output, agent=self)

            return output
        except Exception as e:
            error_msg = f"Agent error: {str(e)}"
            if self.callback_handler:
                try:
                    self.callback_handler(result={"error": error_msg})
                except TypeError:
                    pass
            return error_msg

    def __call__(self, query: str, **kwargs) -> str:
        """Allow the agent to be called directly."""
        return self.invoke(query, **kwargs)


def create_langchain_agent(
    model: BaseLanguageModel,
    tools: Optional[List[Any]] = None,
    system_prompt: str = "",
    name: str = "Agent",
    agent_id: Optional[str] = None,
    callback_handler: Optional[Callable] = None,
    **kwargs,
) -> LangChainAgent:
    """
    Factory function to create a LangChain agent using native functions.

    This function creates a LangChainAgent that uses LangChain's native
    tool-calling agent creation functions.

    Args:
        model: LangChain LLM model
        tools: List of tools (can be Strands or LangChain tools)
        system_prompt: System prompt for the agent
        name: Agent name
        agent_id: Unique agent ID (auto-generated if not provided)
        callback_handler: Optional callback handler
        **kwargs: Additional arguments (ignored for compatibility)

    Returns:
        LangChainAgent instance
    """
    # Convert tools to LangChain format if needed
    if tools:
        langchain_tools = []
        for tool in tools:
            # Check if it's already a LangChain tool
            if isinstance(tool, BaseTool):
                langchain_tools.append(tool)
            elif hasattr(tool, "tool_name"):
                # This is a Strands tool, try to convert it
                # For now, we'll skip Strands tools as they should be converted beforehand
                continue
            else:
                langchain_tools.append(tool)
        tools = langchain_tools
    else:
        tools = []

    return LangChainAgent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        name=name,
        agent_id=agent_id,
        callback_handler=callback_handler,
        **kwargs,
    )

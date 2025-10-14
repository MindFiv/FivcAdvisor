"""
Chat manager for handling conversation state and agent execution.

This module provides ChatManager class to replace the old ChatSession,
with a cleaner interface and support for task notifications.
"""

import uuid
from functools import cached_property
from typing import Optional, Callable, List

from fivcadvisor import agents, tools, settings, utils
from fivcadvisor.agents.types import (
    AgentsRuntime,
    AgentsMonitorManager,
)
from fivcadvisor.agents.types.repositories import (
    # AgentsRuntimeRepository,
    FileAgentsRuntimeRepository,
)


class ChatManager(object):
    """
    Manages chat conversation state and agent execution.

    This is a complete rewrite of ChatSession with a cleaner interface
    and support for task notifications.

    Attributes:
        tools_retriever: Retriever for tool access
        runtime_repo: Repository for persisting agent runtime state
        monitor_manager: Manager for creating and monitoring agent executions
        session_id: Unique session identifier
        agent_id: Unique agent identifier
    """

    def __init__(
        self,
        tools_retriever: Optional[tools.ToolsRetriever] = None,
    ):
        """
        Initialize ChatManager.

        Args:
            tools_retriever: Retriever for tool access (required)
        """

        assert tools_retriever is not None

        self.tools_retriever = tools_retriever
        self.runtime_repo = FileAgentsRuntimeRepository()
        self.monitor_manager = AgentsMonitorManager(
            runtime_repo=self.runtime_repo,
        )

        # Notification queue
        # self.completed_tasks: List[TaskRuntime] = []

        # Execution state
        self.running = False

    @property
    def is_running(self):
        """
        Check if the agent is currently processing a query.

        Returns:
            bool: True if agent is running, False otherwise
        """
        return self.running

    @cached_property
    def session_id(self):
        """
        Get or create a unique session identifier.

        The session ID is cached and persisted in run.yml. Once created,
        it remains the same until cleanup() is called.

        Returns:
            str: UUID string for the current session
        """
        with utils.OutputDir():
            config = settings.SettingsConfig("run.yml")
            session_id = config.get("session_id")
            if not session_id:
                session_id = str(uuid.uuid4())
                config.set("session_id", session_id)
                config.save()
        return session_id

    @cached_property
    def agent_id(self):
        """
        Get or create a unique agent identifier.

        The agent ID is cached and persisted in run.yml. Once created,
        it remains the same until cleanup() is called. This ID is used
        to track all agent runtimes for this chat session.

        Returns:
            str: UUID string for the current agent
        """
        with utils.OutputDir():
            config = settings.SettingsConfig("run.yml")
            agent_id = config.get("agent_id")
            if not agent_id:
                agent_id = str(uuid.uuid4())
                config.set("agent_id", agent_id)
                config.save()
        return agent_id

    def list_history(self) -> List[AgentsRuntime]:
        """
        List all completed agent runtimes.

        Returns:
            List of AgentsRuntime instances
        """
        agent_runtimes = self.runtime_repo.list_agent_runtimes(
            self.agent_id,
        )
        return [runtime for runtime in agent_runtimes if runtime.is_completed]

    async def ask(
        self,
        query: str,
        on_event: Optional[Callable[[AgentsRuntime], None]] = None,
    ):
        """
        Send a message to the agent and get response.

        Args:
            query: User query to send
            on_event: Optional callback for streaming events.
                      Receives AgentsRuntime with streaming_text, tool_calls, etc.

        Returns:
            AgentResult from the agent execution

        Raises:
            ValueError: If agent is already running
        """
        if self.running:
            raise ValueError("Agent is already processing a query")

        try:
            # Create agent runtime with monitoring
            self.running = True
            agent = self.monitor_manager.create_agent_runtime(
                query=query,
                agent_id=self.agent_id,
                agent_creator=agents.default_retriever.get("Companion"),
                tools_retriever=self.tools_retriever,
                on_event=on_event,
            )
            return await agent.invoke_async(query)

        finally:
            self.running = False

    def cleanup(self) -> None:
        """
        Clear conversation history and start a new session.

        This creates a new session ID by clearing the cached property.
        Previous agent runtimes remain in the repository for history.
        """
        # Clear cached session_id and agent_id to force new ones
        if "session_id" in self.__dict__:
            del self.__dict__["session_id"]
        if "agent_id" in self.__dict__:
            del self.__dict__["agent_id"]

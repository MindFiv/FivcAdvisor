"""
Agent execution monitor for tracking single-agent execution.

This module provides monitoring and management classes for agent execution:

Core Classes:
    - AgentsMonitor: Tracks single agent execution through callback events
    - AgentsMonitorManager: Manages multiple agent executions with persistence

Features:
    - Real-time streaming text accumulation
    - Tool call event capture with status tracking
    - Unified callback pattern for execution events
    - Framework-agnostic design (no UI dependencies)
    - Graceful error handling for callbacks
    - Automatic persistence via AgentsRuntimeRepository
    - Conversation history management
    - Multi-turn agent support

Callback Pattern:
    The monitor uses a unified callback pattern where a single on_event callback
    receives the complete AgentsRuntime state after each event, allowing UI
    components to access all execution data in one place.

Integration with AgentsRunnable:
    AgentsMonitor integrates with AgentsRunnable through callback_handler parameter,
    capturing execution events and maintaining runtime state. The monitor receives
    string responses from AgentsRunnable and stores them in the runtime.

Key Features:
    - Unified callback-based execution tracking via AgentsRuntime
    - Real-time streaming message accumulation
    - Tool call event capture with status tracking
    - Framework-agnostic design (no UI dependencies)
    - Graceful error handling for callbacks
    - Cleanup method for resetting state between executions
    - Centralized agent lifecycle management through AgentsMonitorManager
    - Automatic agent creation with monitoring integration
"""

from datetime import datetime
from typing import Any, Optional, List, Callable, Tuple
from uuid import uuid4

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessageChunk, AIMessageChunk, ToolMessage

from fivcadvisor import agents, tools
from fivcadvisor.agents.types.base import (
    AgentsRuntime,
    AgentsRuntimeToolCall,
    AgentsStatus,
)
from fivcadvisor.agents.types.repositories import (
    AgentsRuntimeRepository,
)


class AgentsMonitor(BaseCallbackHandler):
    """
    Agent execution monitor for tracking single-agent execution.

    Tracks agent execution through callback events, capturing streaming text
    chunks and execution state in an AgentsRuntime object. Provides real-time
    callbacks for UI updates while maintaining framework-agnostic design.

    Integration with AgentsRunnable:
    The monitor is passed as callback_handler to AgentsRunnable and receives
    execution events through the __call__ method with different modes:
    - "start": Execution started
    - "messages": Streaming message chunks
    - "values": Final output values (including structured_response or messages)
    - "updates": State updates
    - "finish": Execution completed

    All events are accumulated in an AgentsRuntime object that tracks:
    - Streaming text accumulation
    - Tool call execution with status tracking
    - Overall execution status
    - Final reply (string or structured response)

    Properties:
        id: Unique identifier from the runtime
        is_completed: Whether execution is complete
        status: Current execution status
        tool_calls: List of all tool calls from the runtime

    Usage:
        >>> from fivcadvisor.agents.types import AgentsMonitor, AgentsRuntime
        >>> from fivcadvisor import agents
        >>>
        >>> # Create monitor with optional event callback
        >>> def on_event(runtime: AgentsRuntime):
        ...     # Access streaming text
        ...     print(f"Streaming: {runtime.streaming_text}", end="", flush=True)
        ...
        ...     # Access final reply
        ...     if runtime.reply:
        ...         print(f"Reply: {runtime.reply}")
        >>>
        >>> monitor = AgentsMonitor(on_event=on_event)
        >>>
        >>> # Create agent with monitor as callback handler
        >>> agent = agents.create_companion_agent(callback_handler=monitor)
        >>>
        >>> # Execute and monitor automatically tracks execution
        >>> result = agent.run("What is 2+2?")
        >>>
        >>> # Access accumulated state via tool_calls property
        >>> tools = monitor.tool_calls
        >>>
        >>> # Reset for next execution with new callback
        >>> monitor.cleanup(on_event=on_event)

    Callback Events:
        The monitor receives events through __call__ method with different modes:
        - "start": Execution started, initializes runtime state
        - "messages": Streaming message chunks, accumulates streaming_text
        - "values": Final output values, stores reply (string or structured response)
        - "updates": State updates, clears streaming_text
        - "finish": Execution completed, marks status as COMPLETED
    """

    @property
    def id(self):
        return self._runtime.id

    @property
    def is_completed(self) -> bool:
        return self._runtime.is_completed

    @property
    def status(self) -> AgentsStatus:
        return self._runtime.status

    def __init__(
        self,
        runtime: Optional[AgentsRuntime] = None,
        runtime_repo: Optional[AgentsRuntimeRepository] = None,
        on_event: Optional[Callable[[AgentsRuntime], None]] = None,
    ):
        """
        Initialize AgentsMonitor.

        Args:
            runtime: Optional AgentsRuntime instance to track execution state.
                     If not provided, a new AgentsRuntime will be created.
            runtime_repo: Optional repository for persisting agent runtime state.
                         If not provided, a default FileAgentsRuntimeRepository will be created.
            on_event: Optional callback invoked after each event (streaming or tool).
                      Receives the complete AgentsRuntime state, allowing access to
                      streaming_text, tool_calls, and other execution metadata.
        """
        from fivcadvisor.agents.types.repositories.files import (
            FileAgentsRuntimeRepository,
        )

        self._runtime = runtime or AgentsRuntime()
        self._repo = runtime_repo or FileAgentsRuntimeRepository()
        self._on_event = on_event

        if not runtime:
            self._repo.update_agent_runtime(
                self._runtime.agent_id or "unknown", self._runtime
            )

    def on_start(self):
        self._runtime.reply = None
        self._runtime.status = AgentsStatus.EXECUTING
        self._runtime.started_at = datetime.now()
        self._repo.update_agent_runtime(self._runtime.agent_id, self._runtime)

        if self._on_event:
            self._on_event(self._runtime)

    def on_finish(self):
        self._runtime.status = AgentsStatus.COMPLETED
        self._runtime.completed_at = datetime.now()
        self._repo.update_agent_runtime(self._runtime.agent_id, self._runtime)

        if self._on_event:
            self._on_event(self._runtime)

    def on_updates(self, event: dict[str, Any]):
        # print(f"on_updates {event}")
        self._runtime.streaming_text = ""

    def on_values(self, event: dict[str, Any]):
        if "structured_response" in event:
            self._runtime.reply = event["structured_response"]

        elif "messages" in event:
            self._runtime.reply = event["messages"][-1]

        self._repo.update_agent_runtime(self._runtime.agent_id, self._runtime)

        if self._on_event:
            self._on_event(self._runtime)

    def on_messages(self, event: Tuple[BaseMessageChunk, dict]):
        msg, _ = event

        if isinstance(msg, AIMessageChunk):
            self._runtime.streaming_text += msg.text

        elif isinstance(msg, ToolMessage):
            tool_call = AgentsRuntimeToolCall(
                tool_use_id=msg.tool_call_id,
                tool_name=msg.name,
                # tool_input=msg.input,
                tool_result=msg.content,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                status=msg.status,
            )
            # print(msg.model_dump_json())
            self._runtime.tool_calls[tool_call.tool_use_id] = tool_call
            self._repo.update_agent_runtime_tool_call(
                self._runtime.agent_id or "unknown",
                self._runtime.agent_run_id,
                tool_call,
            )

        # self._repo.update_agent_runtime(self._runtime.agent_id, self._runtime)

        if self._on_event:
            self._on_event(self._runtime)

    def __call__(self, mode: str, event: Any) -> None:
        try:
            if mode == "messages":
                self.on_messages(event)
            elif mode == "values":
                self.on_values(event)
            elif mode == "updates":
                self.on_updates(event)
            elif mode == "start":
                self.on_start()
            elif mode == "finish":
                self.on_finish()

        except Exception as e:
            # Gracefully handle callback exceptions
            import traceback

            print(f"Error in monitor callback: {e} {traceback.format_exc()}")

    @property
    def tool_calls(self) -> List[AgentsRuntimeToolCall]:
        """
        Get list of all tool calls from the runtime.

        Returns:
            List of AgentsRuntimeToolCall instances representing all tool
            invocations during the current execution.
        """
        return list(self._runtime.tool_calls.values())

    def cleanup(
        self,
        runtime: Optional[AgentsRuntime] = None,
        on_event: Optional[Callable[[AgentsRuntime], None]] = None,
    ) -> None:
        """
        Reset monitor state for a new execution.

        Replaces the current runtime with a new one (or the provided runtime)
        and optionally updates the event callback. This is typically called
        before starting a new agent execution to clear previous state.

        Args:
            runtime: Optional new AgentsRuntime instance. If not provided,
                     a fresh AgentsRuntime will be created.
            on_event: Optional new event callback. If not provided, the
                      callback will be cleared (set to None).
        """
        self._runtime = runtime or AgentsRuntime()
        self._on_event = on_event


class AgentsMonitorManager(object):
    """
    Centralized agent monitor manager for creating and monitoring agent executions.

    AgentsMonitorManager provides a unified interface to:
    - Create agents with automatic monitoring integration
    - Retrieve tools based on query context
    - Track agent execution status through AgentsMonitor
    - Persist agent execution history through AgentsRuntimeRepository

    Usage:
        >>> from fivcadvisor.agents.types.monitors import AgentsMonitorManager
        >>> from fivcadvisor.agents.types.repositories.files import FileAgentsRuntimeRepository
        >>> from fivcadvisor.agents.types import agent_creator
        >>> from fivcadvisor import tools
        >>> from fivcadvisor.utils import OutputDir
        >>>
        >>> # Create manager with file-based persistence
        >>> repo = FileAgentsRuntimeRepository(output_dir=OutputDir("./agents"))
        >>> manager = AgentsMonitorManager(runtime_repo=repo)
        >>>
        >>> # Create an agent with automatic monitoring
        >>> agent = manager.create_agent_runtime(
        ...     query="What is the weather today?",
        ...     tools_retriever=tools.default_retriever,
        ...     agent_creator=agent_creator("companion")
        ... )
        >>>
        >>> # Execute agent (monitoring happens automatically)
        >>> result = await agent.invoke_async("What is the weather today?")
        >>>
        >>> # View all agent executions
        >>> monitors = manager.list_agent_runtimes(agent_id)  # Returns list of AgentsMonitor
        >>>
        >>> # Get specific agent execution monitor
        >>> agent_monitor = manager.get_agent_runtime(agent_id, agent_run_id)
        >>> print(f"Status: {agent_monitor.status}")
        >>> print(f"Tool calls: {len(agent_monitor.tool_calls)}")
        >>>
        >>> # Delete an agent execution
        >>> manager.delete_agent_runtime(agent_id, agent_run_id)

    Note:
        The runtime_repo parameter is required.
        Previous agent messages are automatically loaded from the repository and
        passed to the agent creator for conversation continuity.
    """

    def __init__(
        self,
        runtime_repo: Optional["AgentsRuntimeRepository"] = None,
        **kwargs,
    ):
        """
        Initialize AgentsMonitorManager.

        Args:
            runtime_repo: AgentsRuntimeRepository instance for persisting agent runtime state.
                         Required parameter for tracking and storing agent execution history.
            **kwargs: Additional keyword arguments (reserved for future use)

        Raises:
            AssertionError: If runtime_repo is None

        Example:
            >>> from fivcadvisor.agents.types.repositories.files import FileAgentsRuntimeRepository
            >>> from fivcadvisor.utils import OutputDir
            >>>
            >>> repo = FileAgentsRuntimeRepository(output_dir=OutputDir("./agents"))
            >>> manager = AgentsMonitorManager(runtime_repo=repo)
        """
        assert runtime_repo is not None, "runtime_repo is required"

        self._repo = runtime_repo

    def create_agent_runtime(
        self,
        query: str,
        tools_retriever: Optional["tools.ToolsRetriever"] = None,
        agent_id: Optional[str] = None,
        agent_creator: Optional["agents.AgentsCreatorBase"] = None,
        on_event: Optional[Callable[[AgentsRuntime], None]] = None,
        **kwargs,
    ) -> Any:
        """
        Create a new agent runtime with automatic monitoring integration.

        This method:
        1. Retrieves relevant tools based on the query
        2. Generates a unique agent ID (if not provided)
        3. Loads previous completed messages from the repository for conversation continuity
        4. Creates an AgentsRuntime to track execution
        5. Creates an AgentsMonitor as callback handler
        6. Creates the agent using the provided agent_creator with:
           - Previous messages for conversation history
           - The manager's conversation_manager for conversation management
           - The monitor as callback_handler for execution tracking
        7. Persists the initial runtime state

        Args:
            query: The query/task for the agent to execute. Used for tool retrieval
                  and stored in the AgentsRuntime for reference.
            tools_retriever: ToolsRetriever to get relevant tools for the query.
                           Required parameter.
            agent_id: Optional unique identifier for the agent. If not provided,
                     a UUID will be auto-generated.
            agent_creator: AgentsCreatorBase to create the agent instance.
                          Should be a callable that accepts agent_id, agent_name,
                          messages, conversation_manager, callback_handler,
                          tools, and additional kwargs. Required parameter.
            on_event: Optional callback invoked with AgentsRuntime after each agent event.
                     Useful for UI updates or logging. The callback receives the complete
                     runtime state including streaming_text, tool_calls, and status.
            **kwargs: Additional arguments passed to agent_creator

        Returns:
            Agent instance with monitoring already configured

        Raises:
            AssertionError: If tools_retriever or agent_creator is None
            ValueError: If agent creation fails

        Example:
            >>> from fivcadvisor.agents.types import agent_creator
            >>> from fivcadvisor import tools
            >>> from fivcadvisor.agents.types.repositories.files import FileAgentsRuntimeRepository
            >>> from fivcadvisor.utils import OutputDir
            >>>
            >>> # Setup manager
            >>> repo = FileAgentsRuntimeRepository(output_dir=OutputDir("./agents"))
            >>> manager = AgentsMonitorManager(runtime_repo=repo)
            >>>
            >>> # Create agent with custom ID
            >>> agent = manager.create_agent_runtime(
            ...     query="What is 2+2?",
            ...     agent_id="calc-agent-001",
            ...     tools_retriever=tools.default_retriever,
            ...     agent_creator=agent_creator("companion")
            ... )
            >>> result = await agent.run_async("What is 2+2?")
        """
        assert tools_retriever is not None
        assert agent_creator is not None

        # Retrieve tools according to query
        agent_tools = tools_retriever.retrieve(query)
        agent_tool_names = [i.name for i in agent_tools]
        print(f"Agent Tools: {agent_tool_names} for query: {query}")

        # Generate unique agent ID
        agent_id = agent_id or str(uuid4())

        # Sync runtime to agent
        agent_runtimes = self._repo.list_agent_runtimes(agent_id)
        agent_messages = [
            runtime.reply
            for runtime in agent_runtimes
            if (runtime.is_completed and runtime.reply)
        ]

        # Create runtime to track execution
        agent_runtime = AgentsRuntime(
            query=query,
            agent_id=agent_id,
            agent_name=agent_creator.name,
        )

        # Create monitor as callback handler
        agent_monitor = AgentsMonitor(
            on_event=on_event,
            runtime=agent_runtime,
            runtime_repo=self._repo,
        )

        # Create agent with monitoring
        agent = agent_creator(
            agent_id=agent_id,
            agent_name=agent_creator.name,
            messages=agent_messages,
            callback_handler=agent_monitor,
            tools=agent_tools,
            **kwargs,
        )

        if not agent:
            raise ValueError("Agent creation failed")

        # Persist initial runtime state
        self._repo.update_agent_runtime(agent_id, agent_runtime)

        return agent

    def list_agent_runtimes(
        self, agent_id: str, status: Optional[List[AgentsStatus]] = None
    ) -> List[AgentsMonitor]:
        """
        Get list of all agent runtime monitors.

        Args:
            agent_id: Agent ID to list runtimes for
            status: Optional list of statuses to filter by

        Returns:
            List of AgentsMonitor instances
        """
        agent_runtimes = self._repo.list_agent_runtimes(agent_id)
        if status:
            return [
                AgentsMonitor(runtime=runtime, runtime_repo=self._repo)
                for runtime in agent_runtimes
                if runtime.status in status
            ]

        else:
            return [
                AgentsMonitor(runtime=runtime, runtime_repo=self._repo)
                for runtime in agent_runtimes
            ]

    def get_agent_runtime(
        self,
        agent_id: str,
        agent_run_id: str,
        on_event: Optional[Callable[[AgentsRuntime], None]] = None,
    ) -> Optional[AgentsMonitor]:
        """
        Get an agent runtime monitor by ID.

        Args:
            agent_id: Agent ID to retrieve
            agent_run_id: Agent run ID to retrieve
            on_event: Optional callback invoked with AgentsRuntime after each agent event

        Returns:
            AgentsMonitor instance or None if not found
        """
        agent_runtime = self._repo.get_agent_runtime(agent_id, agent_run_id)
        if not agent_runtime:
            return None

        return AgentsMonitor(
            runtime=agent_runtime,
            runtime_repo=self._repo,
            on_event=on_event,
        )

    def delete_agent_runtime(self, agent_id: str, agent_run_id: str) -> None:
        """
        Delete an agent runtime execution.

        Args:
            agent_id: Agent ID to delete
            agent_run_id: Agent run ID to delete
        """
        self._repo.delete_agent_runtime(agent_id, agent_run_id)

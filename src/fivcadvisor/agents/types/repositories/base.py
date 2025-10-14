from abc import ABC, abstractmethod
from typing import Optional, List

from fivcadvisor.agents.types import (
    AgentsRuntime,
    AgentsRuntimeToolCall,
)


class AgentsRuntimeRepository(ABC):
    """
    Abstract base class for agent runtime data repositories.

    Defines the interface for persisting and retrieving agent execution data.
    Implementations can use different storage backends (files, databases, etc.).
    """

    @abstractmethod
    def update_agent_runtime(self, agent_id: str, agent_runtime: AgentsRuntime) -> None:
        """Create or update an agent runtime's metadata."""
        ...

    @abstractmethod
    def get_agent_runtime(
        self, agent_id: str, agent_run_id: str
    ) -> Optional[AgentsRuntime]:
        """Retrieve an agent runtime by agent ID."""
        ...

    @abstractmethod
    def delete_agent_runtime(self, agent_id: str, agent_run_id: str) -> None:
        """Delete an agent runtime and all its tool calls."""
        ...

    @abstractmethod
    def list_agent_runtimes(self, agent_id: str) -> List[AgentsRuntime]:
        """List all agent runtimes in the repository."""
        ...

    @abstractmethod
    def get_agent_runtime_tool_call(
        self, agent_id: str, agent_run_id: str, tool_call_id: str
    ) -> Optional[AgentsRuntimeToolCall]:
        """Retrieve a specific tool call by agent ID and tool call ID."""
        ...

    @abstractmethod
    def update_agent_runtime_tool_call(
        self, agent_id: str, agent_run_id: str, tool_call: AgentsRuntimeToolCall
    ) -> None:
        """Create or update a tool call for an agent runtime."""
        ...

    @abstractmethod
    def list_agent_runtime_tool_calls(
        self, agent_id: str, agent_run_id: str
    ) -> List[AgentsRuntimeToolCall]:
        """List all tool calls for an agent runtime."""
        ...

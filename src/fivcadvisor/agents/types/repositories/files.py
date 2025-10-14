"""
File-based agent runtime repository implementation.

This module provides FileAgentsRuntimeRepository, a file-based implementation
of AgentsRuntimeRepository that stores agent data in a hierarchical directory
structure with JSON files.

Storage Structure:
    /<output_dir>/
    └── agent_<agent_id>/
        └── run_<agent_run_id>/
            ├── run.json              # Agent Runtime metadata
            └── tool_calls/
                ├── tool_call_<tool_call_id>.json
                └── tool_call_<tool_call_id>.json

This structure allows for:
    - Multiple runs per agent
    - Easy inspection of agent data
    - Efficient tool-call-by-tool-call updates
    - Simple backup and version control
    - Human-readable JSON format
"""

import json
import shutil
from pathlib import Path
from typing import Optional, List

from fivcadvisor.utils import OutputDir

from fivcadvisor.agents.types.repositories import (
    AgentsRuntime,
    AgentsRuntimeToolCall,
    AgentsRuntimeRepository,
)


class FileAgentsRuntimeRepository(AgentsRuntimeRepository):
    """
    File-based repository for agent runtime data.

    Storage structure:
    /<output_dir>/
    └── agent_<agent_id>/
        └── run_<agent_run_id>/
            ├── run.json              # Agent Runtime metadata
            └── tool_calls/
                ├── tool_call_<tool_call_id>.json
                └── tool_call_<tool_call_id>.json
    """

    def __init__(self, output_dir: Optional[OutputDir] = None):
        self.output_dir = output_dir or OutputDir().subdir("agents")
        self.base_path = Path(str(self.output_dir))
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_agent_dir(self, agent_id: str) -> Path:
        """Get the directory path for an agent."""
        return self.base_path / f"agent_{agent_id}"

    def _get_run_dir(self, agent_id: str, agent_run_id: str) -> Path:
        """Get the directory path for an agent run."""
        return self._get_agent_dir(agent_id) / f"run_{agent_run_id}"

    def _get_run_file(self, agent_id: str, agent_run_id: str) -> Path:
        """Get the file path for agent runtime metadata."""
        return self._get_run_dir(agent_id, agent_run_id) / "run.json"

    def _get_tool_calls_dir(self, agent_id: str, agent_run_id: str) -> Path:
        """Get the directory path for agent tool calls."""
        return self._get_run_dir(agent_id, agent_run_id) / "tool_calls"

    def _get_tool_call_file(
        self, agent_id: str, agent_run_id: str, tool_call_id: str
    ) -> Path:
        """Get the file path for a tool call."""
        return (
            self._get_tool_calls_dir(agent_id, agent_run_id)
            / f"tool_call_{tool_call_id}.json"
        )

    def update_agent_runtime(self, agent_id: str, agent_runtime: AgentsRuntime) -> None:
        """
        Create or update an agent runtime.

        Args:
            agent_id: Agent ID
            agent_runtime: AgentsRuntime instance to persist
        """
        run_dir = self._get_run_dir(agent_id, str(agent_runtime.agent_run_id))
        run_dir.mkdir(parents=True, exist_ok=True)

        run_file = self._get_run_file(agent_id, str(agent_runtime.agent_run_id))

        # Serialize agent to JSON (exclude tool_calls as they're stored separately)
        agent_data = agent_runtime.model_dump(mode="json", exclude={"tool_calls"})

        with open(run_file, "w", encoding="utf-8") as f:
            json.dump(agent_data, f, indent=2, ensure_ascii=False)

    def get_agent_runtime(
        self, agent_id: str, agent_run_id: str
    ) -> Optional[AgentsRuntime]:
        """
        Retrieve an agent runtime by ID.

        Args:
            agent_id: Agent ID
            agent_run_id: Agent run ID to retrieve

        Returns:
            AgentsRuntime instance or None if not found
        """
        run_file = self._get_run_file(agent_id, agent_run_id)

        if not run_file.exists():
            return None

        try:
            with open(run_file, "r", encoding="utf-8") as f:
                agent_data = json.load(f)

            # Reconstruct AgentsRuntime from JSON
            # Note: tool_calls are loaded separately via list_agent_runtime_tool_calls
            return AgentsRuntime.model_validate(agent_data)
        except (json.JSONDecodeError, ValueError) as e:
            # Log error and return None if file is corrupted
            print(f"Error loading agent {agent_id} run {agent_run_id}: {e}")
            return None

    def delete_agent_runtime(self, agent_id: str, agent_run_id: str) -> None:
        """
        Delete an agent runtime and all its tool calls.

        Args:
            agent_id: Agent ID
            agent_run_id: Agent run ID to delete
        """
        run_dir = self._get_run_dir(agent_id, agent_run_id)

        if run_dir.exists():
            shutil.rmtree(run_dir)

    def list_agent_runtimes(self, agent_id: str) -> List[AgentsRuntime]:
        """
        List all agent runtimes for a specific agent in chronological order.

        Args:
            agent_id: Agent ID to list runtimes for

        Returns:
            List of AgentsRuntime instances sorted by agent_run_id (timestamp) in increasing order
        """
        runtimes = []
        agent_dir = self._get_agent_dir(agent_id)

        if not agent_dir.exists():
            return runtimes

        # Iterate through all run directories for this agent
        for run_dir in agent_dir.glob("run_*"):
            if not run_dir.is_dir():
                continue

            # Extract agent_run_id from directory name
            agent_run_id = run_dir.name.replace("run_", "")

            # Load agent runtime
            runtime = self.get_agent_runtime(agent_id, agent_run_id)
            if runtime:
                runtimes.append(runtime)

        # Sort by agent_run_id (timestamp string) in increasing order
        runtimes.sort(key=lambda r: r.agent_run_id)

        return runtimes

    def get_agent_runtime_tool_call(
        self, agent_id: str, agent_run_id: str, tool_call_id: str
    ) -> Optional[AgentsRuntimeToolCall]:
        """
        Retrieve a tool call by agent ID, run ID, and tool call ID.

        Args:
            agent_id: Agent ID
            agent_run_id: Agent run ID
            tool_call_id: Tool call ID

        Returns:
            AgentsRuntimeToolCall instance or None if not found
        """
        tool_call_file = self._get_tool_call_file(agent_id, agent_run_id, tool_call_id)

        if not tool_call_file.exists():
            return None

        try:
            with open(tool_call_file, "r", encoding="utf-8") as f:
                tool_call_data = json.load(f)

            # Reconstruct AgentsRuntimeToolCall from JSON
            return AgentsRuntimeToolCall.model_validate(tool_call_data)
        except (json.JSONDecodeError, ValueError) as e:
            # Log error and return None if file is corrupted
            print(
                f"Error loading tool call {tool_call_id} for agent {agent_id} run {agent_run_id}: {e}"
            )
            return None

    def update_agent_runtime_tool_call(
        self, agent_id: str, agent_run_id: str, tool_call: AgentsRuntimeToolCall
    ) -> None:
        """
        Create or update a tool call.

        Args:
            agent_id: Agent ID
            agent_run_id: Agent run ID
            tool_call: AgentsRuntimeToolCall instance to persist
        """
        tool_calls_dir = self._get_tool_calls_dir(agent_id, agent_run_id)
        tool_calls_dir.mkdir(parents=True, exist_ok=True)

        tool_call_file = self._get_tool_call_file(
            agent_id, agent_run_id, tool_call.tool_use_id
        )

        # Serialize tool call to JSON
        tool_call_data = tool_call.model_dump(mode="json")

        with open(tool_call_file, "w", encoding="utf-8") as f:
            json.dump(tool_call_data, f, indent=2, ensure_ascii=False)

    def list_agent_runtime_tool_calls(
        self, agent_id: str, agent_run_id: str
    ) -> List[AgentsRuntimeToolCall]:
        """
        List all tool calls for an agent runtime.

        Args:
            agent_id: Agent ID
            agent_run_id: Agent run ID

        Returns:
            List of AgentsRuntimeToolCall instances
        """
        tool_calls = []
        tool_calls_dir = self._get_tool_calls_dir(agent_id, agent_run_id)

        if not tool_calls_dir.exists():
            return tool_calls

        # Iterate through all tool call files
        for tool_call_file in tool_calls_dir.glob("tool_call_*.json"):
            if not tool_call_file.is_file():
                continue

            # Extract tool_call_id from file name
            tool_call_id = tool_call_file.stem.replace("tool_call_", "")

            # Load tool call
            tool_call = self.get_agent_runtime_tool_call(
                agent_id, agent_run_id, tool_call_id
            )
            if tool_call:
                tool_calls.append(tool_call)

        return tool_calls

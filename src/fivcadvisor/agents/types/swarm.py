"""
DEPRECATED: Swarm module has been replaced with AgentsSwarmRunnable.

This module is deprecated and will be removed in a future version.
Please use AgentsSwarmRunnable from fivcadvisor.agents.types.runnables instead.

Migration Guide:
    Old (deprecated):
        from fivcadvisor.agents.types.swarm import LangGraphSwarm, create_swarm
        swarm = create_swarm(agents=[...])

    New (recommended):
        from fivcadvisor.agents.types import AgentsSwarmRunnable
        swarm = AgentsSwarmRunnable(agents=[...])

For more information, see the migration guide in the documentation.
"""

import warnings
from typing import Any, List, Optional

# Issue deprecation warning when this module is imported
warnings.warn(
    "The swarm module is deprecated. Use AgentsSwarmRunnable from "
    "fivcadvisor.agents.types.runnables instead.",
    DeprecationWarning,
    stacklevel=2,
)


class LangGraphSwarm:
    """
    DEPRECATED: Use AgentsSwarmRunnable instead.

    This class is deprecated and will be removed in a future version.
    Please use AgentsSwarmRunnable from fivcadvisor.agents.types.runnables instead.
    """

    def __init__(
        self, agents: List[Any], default_agent_name: Optional[str] = None, **kwargs
    ):
        """
        DEPRECATED: Initialize the LangGraph Swarm.

        This class is deprecated. Use AgentsSwarmRunnable instead.

        Args:
            agents: List of LangChain agents to include in the swarm
            default_agent_name: Name of the default agent to start with
            **kwargs: Additional arguments (for future compatibility)
        """
        warnings.warn(
            "LangGraphSwarm is deprecated. Use AgentsSwarmRunnable from "
            "fivcadvisor.agents.types.runnables instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        raise NotImplementedError(
            "LangGraphSwarm has been removed. "
            "Please use AgentsSwarmRunnable from fivcadvisor.agents.types.runnables instead. "
            "See migration guide in documentation."
        )


def create_swarm(
    agents: List[Any], default_agent_name: Optional[str] = None, **kwargs
) -> "LangGraphSwarm":
    """
    DEPRECATED: Use AgentsSwarmRunnable instead.

    This function is deprecated and will be removed in a future version.
    Please use AgentsSwarmRunnable from fivcadvisor.agents.types.runnables instead.

    Args:
        agents: List of LangChain agents to include in the swarm.
        default_agent_name: Name of the default agent to start with.
        **kwargs: Additional arguments for future compatibility

    Raises:
        NotImplementedError: Always raises, as this function is deprecated.
    """
    warnings.warn(
        "create_swarm is deprecated. Use AgentsSwarmRunnable from "
        "fivcadvisor.agents.types.runnables instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError(
        "create_swarm has been removed. "
        "Please use AgentsSwarmRunnable from fivcadvisor.agents.types.runnables instead. "
        "See migration guide in documentation."
    )


# Backward compatibility alias (also deprecated)
LangGraphSwarmAdapter = LangGraphSwarm

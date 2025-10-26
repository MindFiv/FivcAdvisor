__all__ = [
    "create_default_agent",
    "create_companion_agent",
    "create_tooling_agent",
    "create_consultant_agent",
    "create_planning_agent",
    "create_research_agent",
    "create_engineering_agent",
    "create_evaluating_agent",
    "create_generic_agent_swarm",
    "default_retriever",
    "default_agent",
    "AgentsRetriever",
]

from typing import cast, List, Optional, Any
from uuid import uuid4
# from typing import Callable

from fivcadvisor import (
    tools,
    utils,
)
from fivcadvisor.models import (
    create_default_model,
    create_chat_model,
    create_reasoning_model,
)
from fivcadvisor.tasks.types import TaskTeam
from fivcadvisor.agents.types import (
    agent_creator,
    AgentsRetriever,
    AgentsCreatorBase,
)
from fivcadvisor.agents.types.langchain_agent import create_langchain_agent
from fivcadvisor.agents.types.swarm import LangGraphSwarm

# Backward compatibility alias
LangGraphSwarmAdapter = LangGraphSwarm


@agent_creator("Generic")
def create_default_agent(*args, **kwargs) -> Any:
    """Create a standard ReAct agent for task execution."""

    # filter out unknown kwargs
    kwargs = {
        k: v
        for k, v in kwargs.items()
        if k
        in [
            "model",
            "messages",
            "tools",
            "system_prompt",
            "callback_handler",
            "conversation_manager",
            "record_direct_tool_call",
            "load_tools_from_directory",
            "trace_attributes",
            "agent_id",
            "name",
            "description",
            "state",
            "hooks",
            "session_manager",
            "tool_executor",
        ]
    }

    # Set default role if not provided
    kwargs.setdefault("name", "Generic")

    if "agent_id" not in kwargs:
        kwargs["agent_id"] = str(uuid4())

    if "tools" not in kwargs:
        kwargs["tools"] = tools.default_retriever.get_all()

    if "model" not in kwargs:
        kwargs["model"] = create_default_model()

    # Use LangChain Agent adapter instead of Strands Agent
    agent = create_langchain_agent(*args, **kwargs)

    return agent


@agent_creator("Companion")
def create_companion_agent(*args, **kwargs) -> Any:
    """Create a friend agent for chat."""
    kwargs["name"] = "Companion"
    kwargs.setdefault(
        "system_prompt", "You are a companion, or even a close friend of the user. "
    )
    if "model" not in kwargs:
        kwargs["model"] = create_chat_model()

    if "tools" not in kwargs:
        kwargs["tools"] = tools.default_retriever.get_all()

    return create_default_agent(*args, **kwargs)


@agent_creator("ToolRetriever")
def create_tooling_agent(*args, **kwargs) -> Any:
    """Create an agent that can retrieve tools."""
    kwargs["name"] = "ToolRetriever"
    kwargs.setdefault(
        "system_prompt",
        "You are a tool retrieval specialist with deep expertise "
        "in identifying the most appropriate tools for a given task. "
        "Skilled at quickly assessing task requirements, "
        "analyzing available toolsets, and "
        "selecting the best tools for the job.",
    )

    if "model" not in kwargs:
        kwargs["model"] = create_reasoning_model()

    return create_default_agent(*args, **kwargs)


@agent_creator(name="Consultant")
def create_consultant_agent(*args, **kwargs) -> Any:
    """Create an agent that can assess tasks."""
    kwargs["name"] = "Consultant"
    kwargs.setdefault(
        "system_prompt",
        """
        You are a task assessment specialist with deep expertise in
        determining the best approach for handling a given task.
        Skilled at quickly assessing task requirements, identifying
        the optimal tools and resources needed, or given an answer if
        the task can be handled directly.
        """,
    )
    if "model" not in kwargs:
        kwargs["model"] = create_reasoning_model()

    return create_default_agent(*args, **kwargs)


@agent_creator(name="Planner")
def create_planning_agent(*args, **kwargs) -> Any:
    """Create an agent that can plan tasks."""
    kwargs["name"] = "Planner"
    kwargs.setdefault(
        "system_prompt",
        "You are a task planning specialist with deep expertise "
        "in breaking down complex tasks into manageable components. "
        "Skilled at identifying the optimal crew composition, "
        "task prioritization, and workflow orchestration. "
        "Your goal is to create a plan for executing the task "
        "that is both efficient and effective.",
    )
    return create_default_agent(*args, **kwargs)


@agent_creator(name="Researcher")
def create_research_agent(*args, **kwargs) -> Any:
    """Create an agent that can research tasks."""
    kwargs["name"] = "Researcher"
    kwargs.setdefault(
        "system_prompt",
        "You are a pattern recognition specialist and domain analysis expert "
        "with deep expertise in workflow optimization. "
        "Skilled at identifying recurring task sequences, "
        "analyzing execution patterns across different domains, "
        "and extracting actionable insights from complex data flows. "
        "Experienced in comprehensive logging analysis and "
        "workflow pattern summarization to "
        "drive continuous system improvement.",
    )
    return create_default_agent(*args, **kwargs)


@agent_creator(name="Engineer")
def create_engineering_agent(*args, **kwargs) -> Any:
    """Create an agent that can engineer tools."""
    kwargs["name"] = "Engineer"
    kwargs.setdefault(
        "system_prompt",
        "You are a tool development specialist and code generation expert "
        "with extensive experience in creating composite tools from "
        "existing components. "
        "Skilled at autonomous tool creation, "
        "combining multiple functionalities into cohesive solutions, "
        "and implementing self-improving systems based on usage patterns. "
        "Expert in maintaining toolset ecosystems and "
        "optimizing tool performance for maximum efficiency.",
    )
    return create_default_agent(*args, **kwargs)


@agent_creator(name="Evaluator")
def create_evaluating_agent(*args, **kwargs) -> Any:
    """Create an agent that can evaluate performance."""
    kwargs["name"] = "Evaluator"
    kwargs.setdefault(
        "system_prompt",
        "You are a performance assessment specialist and "
        "quality assurance expert with "
        "deep expertise in automated evaluation systems. "
        "Skilled at monitoring multi-agent workflows, "
        "identifying optimization opportunities, "
        "and implementing human-in-the-loop validation processes. "
        "Expert in performance tracking, "
        "tool effectiveness validation, "
        "and continuous monitoring for decision pattern recognition to "
        "drive system-wide improvements.",
    )
    return create_default_agent(*args, **kwargs)


@agent_creator(name="Generic Swarm")
def create_generic_agent_swarm(
    *args,
    team: Optional[TaskTeam] = None,
    tools_retriever: Optional[tools.ToolsRetriever] = None,
    **kwargs,
) -> Any:
    """
    Create a generic swarm of agents.

    This function creates a swarm of agents using LangGraph Swarm as the
    underlying orchestration engine. It maintains backward compatibility
    with the Strands Swarm API through the LangGraphSwarmAdapter.

    All agents in the swarm use LangChainAgentAdapter for compatibility
    with the LangChain ecosystem.

    Args:
        team: TaskTeam containing specialist definitions
        tools_retriever: ToolsRetriever to fetch tools for each specialist
        **kwargs: Additional arguments passed to agent creation

    Returns:
        LangGraphSwarmAdapter instance (compatible with Swarm API)

    Raises:
        RuntimeError: If team or tools_retriever is not provided
    """
    if not team:
        raise RuntimeError("team not provided")

    if not tools_retriever:
        raise RuntimeError("tools_retriever not provided")

    s_agents = []
    for s in team.specialists:
        s_tools = tools_retriever.get_batch(s.tools)
        s_tools = [t for t in s_tools if t is not None]
        # create_default_agent now returns LangChainAgentAdapter
        s_agents.append(
            create_default_agent(
                name=s.name,
                tools=s_tools,
                system_prompt=s.backstory,
                **kwargs,
            )
        )

    # Use LangGraph Swarm adapter instead of Strands Swarm
    # This maintains the same API while using LangGraph under the hood
    return LangGraphSwarmAdapter(s_agents)


def _load_retriever() -> AgentsRetriever:
    retriever = AgentsRetriever()
    retriever.add_batch(
        cast(
            List[AgentsCreatorBase],
            [
                create_default_agent,
                create_companion_agent,
                create_tooling_agent,
                create_consultant_agent,
                create_planning_agent,
                create_research_agent,
                create_engineering_agent,
                create_evaluating_agent,
                create_generic_agent_swarm,
            ],
        )
    )
    return retriever


default_retriever = utils.create_lazy_value(_load_retriever)
default_agent = utils.create_lazy_value(lambda: create_companion_agent())

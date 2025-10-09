__all__ = [
    "run_tooling_task",
    "run_assessing_task",
    "run_planning_task",
    "run_executing_task",
    "TaskTracer",
    "TaskEvent",
    "TaskStatus",
    "TaskManager",
]

from typing import Optional

from strands.multiagent import SwarmResult

from fivcadvisor import schemas
from fivcadvisor import agents
from fivcadvisor import tools
from fivcadvisor.tasks.types import TaskTracer, TaskEvent, TaskStatus, TaskManager


async def run_tooling_task(
    query: str, tools_retriever: Optional[tools.ToolsRetriever] = None, **kwargs
) -> schemas.TaskRequirement:
    """Run a tooling task for an agent."""
    if "tools" not in kwargs and tools_retriever is not None:
        kwargs["tools"] = [tools_retriever.to_tool()]

    agent = agents.create_tooling_agent(**kwargs)
    agent_prompt = f"Retrieve the best tools for the following task: \n" f"{query}"
    return await agent.structured_output_async(
        schemas.TaskRequirement, prompt=agent_prompt
    )


async def run_assessing_task(
    query: str,
    tools_retriever: Optional[tools.ToolsRetriever] = None,
    **kwargs,
) -> schemas.TaskAssessment:
    """Run an assessing task for an agent."""
    if "tools" not in kwargs and tools_retriever is not None:
        kwargs["tools"] = [tools_retriever.to_tool()]

    agent = agents.create_consultant_agent(**kwargs)
    agent_prompt = (
        f"Assess the following query and determine the best approach for handling it. "
        f"Provide your assessment in JSON format with these exact fields:\n"
        f"- require_planning (bool): Whether a planning agent is required to break down the task. "
        f"Set to true for complex tasks that need multiple steps or specialized agents.\n"
        f"- require_tools (list): List of tool names needed, empty list if none\n"
        f"- reasoning (string): Brief explanation of your assessment\n\n"
        f"Query: {query}"
    )
    return await agent.structured_output_async(
        schemas.TaskAssessment, prompt=agent_prompt
    )


async def run_planning_task(
    query: str,
    tools_retriever: Optional[tools.ToolsRetriever] = None,
    **kwargs,
) -> schemas.TaskTeam:
    """Run a planning task for an agent."""
    if "tools" not in kwargs and tools_retriever is not None:
        kwargs["tools"] = [tools_retriever.to_tool()]

    agent = agents.create_planning_agent(**kwargs)
    agent_prompt = (
        f"Analyze the following query and create a team for execution. "
        f"Provide your response in JSON format with these exact fields:\n"
        f"- specialists (array): List of specialist agents needed for the task\n"
        f"  Each specialist should have:\n"
        f"  - name (string): Name of the agent\n"
        f"  - backstory (string): System prompt/backstory for the agent\n"
        f"  - tools (array): List of tool names the agent needs\n\n"
        f"Query: {query}\n"
    )
    return await agent.structured_output_async(schemas.TaskTeam, prompt=agent_prompt)


async def run_executing_task(
    query: str,
    plan: schemas.TaskTeam,
    tools_retriever: Optional[tools.ToolsRetriever] = None,
    **kwargs,
) -> SwarmResult:
    """Run an execution task using a swarm of agents.

    Args:
        query: The user query to execute
        plan: The TaskTeam plan containing specialist agents
        tools_retriever: Optional tools retriever for agent tools
        **kwargs: Additional arguments to pass to the swarm

    Returns:
        The execution result as a string
    """
    if tools_retriever is None:
        tools_retriever = tools.default_retriever

    # Create a swarm of agents based on the plan
    swarm = agents.create_generic_agent_swarm(
        team=plan, tools_retriever=tools_retriever, **kwargs
    )

    # Execute the query using the swarm
    return await swarm.invoke_async(query)

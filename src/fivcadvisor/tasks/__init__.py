__all__ = [
    "run_tooling_task",
    "run_briefing_task",
    "run_assessing_task",
    "run_planning_task",
    "TaskAssessment",
    "TaskRequirement",
    "TaskTeam",
    "TaskMonitor",
    "TaskRuntimeStep",
    "TaskStatus",
    "TaskMonitorManager",
    "default_manager",
]

from typing import Optional

from fivcadvisor import agents, tools, utils
from fivcadvisor.tasks.types import (
    TaskAssessment,
    TaskRequirement,
    TaskTeam,
    TaskMonitor,
    TaskRuntimeStep,
    TaskStatus,
    TaskMonitorManager,
)


async def run_tooling_task(
    query: str, tools_retriever: Optional[tools.ToolsRetriever] = None, **kwargs
) -> TaskRequirement:
    """Run a tooling task for an agent."""
    if "tools" not in kwargs and tools_retriever is not None:
        kwargs["tools"] = [tools_retriever.to_tool()]

    agent = agents.create_tooling_agent(**kwargs)
    agent_prompt = f"Retrieve the best tools for the following task: \n" f"{query}"
    return await agent.structured_output_async(TaskRequirement, prompt=agent_prompt)


async def run_briefing_task(
    query: str, tools_retriever: Optional[tools.ToolsRetriever] = None, **kwargs
) -> str:
    """Run a summarizing task for an agent."""
    if "tools" not in kwargs and tools_retriever is not None:
        kwargs["tools"] = [tools_retriever.to_tool()]

    agent = agents.create_consultant_agent(**kwargs)
    agent_prompt = (
        f"Summarize the following content and make it brief, "
        f"so that it can be set as a title: \n"
        f"{query}"
    )
    agent_result = await agent.invoke_async(agent_prompt)
    return str(agent_result)


async def run_assessing_task(
    query: str,
    tools_retriever: Optional[tools.ToolsRetriever] = None,
    **kwargs,
) -> TaskAssessment:
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
    return await agent.structured_output_async(TaskAssessment, prompt=agent_prompt)


async def run_planning_task(
    query: str,
    tools_retriever: Optional[tools.ToolsRetriever] = None,
    **kwargs,
) -> TaskTeam:
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
    return await agent.structured_output_async(TaskTeam, prompt=agent_prompt)


default_manager = utils.create_lazy_value(lambda: TaskMonitorManager())

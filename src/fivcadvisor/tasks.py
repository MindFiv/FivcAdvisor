__all__ = [
    "run_tooling_task",
    "run_assessing_task",
    "run_planning_task",
]

from typing import Optional

from fivcadvisor import schemas
from fivcadvisor import agents
from fivcadvisor import tools


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
        f"Assess the following query and determine "
        f"the best approach for handling it: \n"
        f"1. Determine if the query requires a planning agent \n"
        f"2. If not, determine if the query requires a backstory \n"
        f"3. If not, determine if the query requires any tools \n"
        f"4. If it is a simple query, answer the query directly \n"
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
        f"Analyze the flowing query and create a team for execution: \n"
        f"1. Identify what types of specialized agents are needed \n"
        f"2. Provide a backstory as system prompt for each agent \n"
        f"3. Identify the tools each agent needs \n"
        f"Query: {query} \n"
    )
    return await agent.structured_output_async(schemas.TaskTeam, prompt=agent_prompt)

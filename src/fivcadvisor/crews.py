__all__ = [
    "create_simple_crew",
    "create_tooling_crew",
    "create_assessing_crew",
    "create_planning_crew",
    "create_executing_crew",
]

from typing import Optional
from crewai import Crew


class _Crew(Crew):
    session_id: Optional[str] = None


def create_default_crew(*args, session_id=None, **kwargs):
    """
    Create a default crew for handling a task.
    Args:
        *args: Additional arguments passed to Crew constructor
        session_id (str): The session id to use for the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew
    """
    crew = _Crew(*args, **kwargs)
    crew.session_id = session_id
    return crew


def create_simple_crew(
    tools_retriever=None,
    tools_names=None,
    session_id=None,
    **kwargs,
):
    """
    Create a simple crew to handle a task with a single agent.

    Args:
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        tools_names (List[str]): The names of the tools to use for the task
        session_id (str): The session id to use for the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with a single agent and task
    """
    from .llms import create_default_llm
    from .tasks import create_default_task
    from .agents import create_default_agent

    if not tools_retriever:
        raise ValueError("tools_retriever not provided")

    if not isinstance(tools_names, list):
        raise ValueError("tool_names must be a list of strings")

    # if not isinstance(callback, Optional[Callable]):
    #     raise ValueError("callback must be a callable function")

    task_tools = tools_retriever.get_batch(tools_names)
    if None in task_tools:
        raise ValueError("Tools not found for simple task")

    agent = create_default_agent(
        llm=create_default_llm(session_id=session_id),
        session_id=session_id,
    )
    task = create_default_task(
        agent=agent,
        tools=task_tools or None,
        session_id=session_id,
    )
    return create_default_crew(
        agents=[agent],
        tasks=[task],
        session_id=session_id,
        **kwargs,
    )


def create_tooling_crew(
    tools_retriever=None,
    session_id=None,
    **kwargs,
):
    """
    Create a crew to retrieve tools for a task.

    Args:
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        session_id (str): The session id to use for the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with a tooling task
    """

    from .llms import create_reasoning_llm
    from .tasks import create_tooling_task
    from .agents import create_tooling_agent

    if not tools_retriever:
        raise ValueError("tools_retriever not provided")

    agent = create_tooling_agent(
        llm=create_reasoning_llm(
            session_id=session_id,
        ),
        session_id=session_id,
    )
    task = create_tooling_task(
        agent=agent,
        tools=[tools_retriever.to_tool()],
        session_id=session_id,
    )
    return create_default_crew(
        agents=[agent],
        tasks=[task],
        session_id=session_id,
        **kwargs,
    )


def create_assessing_crew(
    tools_retriever=None,
    session_id=None,
    **kwargs,
):
    """
    Create a crew to assess the complexity of a task and determine the best
    approach for handling it.

    Args:
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        session_id (str): The session id to use for the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with an assessment task
    """
    from .llms import create_reasoning_llm
    from .tasks import create_assessing_task
    from .agents import create_consulting_agent

    if not tools_retriever:
        raise ValueError("tools_retriever not provided")

    agent = create_consulting_agent(
        llm=create_reasoning_llm(
            session_id=session_id,
        ),
        session_id=session_id,
    )
    task = create_assessing_task(
        agent=agent,
        tools=[tools_retriever.to_tool()],
        session_id=session_id,
    )
    return create_default_crew(
        agents=[agent],
        tasks=[task],
        session_id=session_id,
        **kwargs,
    )


def create_planning_crew(
    tools_retriever=None,
    session_id=None,
    **kwargs,
):
    """
    Create a crew to plan the execution of a complex task, breaking it down
    into manageable components and identifying the optimal crew composition.

    Args:
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        session_id (str): The session id to use for the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with a planning task
    """
    from .llms import create_reasoning_llm
    from .tasks import create_planning_task
    from .agents import create_directing_agent

    if not tools_retriever:
        raise ValueError("tools_retriever not provided")

    tools = [
        tools_retriever.get("sequentialthinking"),
        tools_retriever.to_tool(),
    ]
    tools = [t for t in tools if t is not None]
    agent = create_directing_agent(
        llm=create_reasoning_llm(session_id=session_id),
        session_id=session_id,
    )
    task = create_planning_task(
        agent=agent,
        tools=tools,
        session_id=session_id,
    )
    return create_default_crew(
        agents=[agent],
        tasks=[task],
        planning=True,
        planning_llm=create_reasoning_llm(session_id=session_id),
        session_id=session_id,
        **kwargs,
    )


def create_executing_crew(
    tools_retriever=None,
    plan=None,
    session_id=None,
    **kwargs,
):
    """
    Create a crew based on a pre-defined plan.

    Args:
        plan (PlanOutput): The plan to use for creating the crew
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        session_id (str): The session id to use for the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with agents and tasks from the plan
    """
    from crewai import Process
    from .llms import (
        create_default_llm,
        create_reasoning_llm,
        create_chat_llm,
    )
    from .agents import create_default_agent
    from .tasks import create_default_task
    from .models import CrewPlan

    if not tools_retriever:
        raise ValueError("tools_retriever not provided")

    if not isinstance(plan, CrewPlan):
        raise ValueError("plan must be an instance of PlanOutput")

    # Create specialist agents based on the plan
    agents = []
    for agent_plan in plan.agents:
        agent_tools = tools_retriever.get_batch(agent_plan.tools)
        agent_tools = [t for t in agent_tools if t is not None]
        agents.append(
            create_default_agent(
                role=agent_plan.role,
                goal=agent_plan.goal,
                backstory=agent_plan.backstory,
                tools=agent_tools or None,
                # allow_delegation=True,
                llm=create_default_llm(session_id=session_id),
                session_id=session_id,
            )
        )

    # Create tasks based on the plan
    tasks = []
    for task_plan in plan.tasks:
        tasks.append(
            create_default_task(
                name=task_plan.name,
                description=task_plan.description,
                expected_output=task_plan.expected_output,
                human_input=task_plan.requires_human,
                session_id=session_id,
            )
        )

    # Create and return the crew
    return create_default_crew(
        manager_llm=create_reasoning_llm(session_id=session_id),
        chat_llm=create_chat_llm(session_id=session_id),
        tasks=tasks,
        agents=agents,
        process=Process.hierarchical,
        # memory=True,
        planning=True,
        planning_llm=create_reasoning_llm(session_id=session_id),
        session_id=session_id,
        **kwargs,
    )

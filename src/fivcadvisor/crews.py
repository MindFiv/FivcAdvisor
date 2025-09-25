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
    run_id: Optional[str] = None


def create_default_crew(*args, run_id=None, **kwargs):
    """
    Create a default crew for handling a task.
    Args:
        *args: Additional arguments passed to Crew constructor
        run_id (str): The session id to use for the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew
    """
    crew = _Crew(*args, **kwargs)
    crew.run_id = run_id
    return crew


def create_simple_crew(
    tools_retriever=None,
    tools_names=None,
    run_id=None,
    **kwargs,
):
    """
    Create a simple crew to handle a task with a single agent.

    Args:
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        tools_names (List[str]): The names of the tools to use for the task
        run_id (str): The session id to use for the crew
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
        llm=create_default_llm(run_id=run_id),
        run_id=run_id,
    )
    task = create_default_task(
        agent=agent,
        tools=task_tools or None,
        run_id=run_id,
    )
    return create_default_crew(
        agents=[agent],
        tasks=[task],
        run_id=run_id,
        **kwargs,
    )


def create_tooling_crew(
    tools_retriever=None,
    run_id=None,
    **kwargs,
):
    """
    Create a crew to retrieve tools for a task.

    Args:
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        run_id (str): The run id to use for the crew
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
            run_id=run_id,
        ),
        run_id=run_id,
    )
    task = create_tooling_task(
        agent=agent,
        tools=[tools_retriever.to_tool()],
        run_id=run_id,
    )
    return create_default_crew(
        agents=[agent],
        tasks=[task],
        run_id=run_id,
        **kwargs,
    )


def create_assessing_crew(
    tools_retriever=None,
    run_id=None,
    **kwargs,
):
    """
    Create a crew to assess the complexity of a task and determine the best
    approach for handling it.

    Args:
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        run_id (str): The run id to use for the crew
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
            run_id=run_id,
        ),
        run_id=run_id,
    )
    task = create_assessing_task(
        agent=agent,
        tools=[tools_retriever.to_tool()],
        run_id=run_id,
    )
    return create_default_crew(
        agents=[agent],
        tasks=[task],
        run_id=run_id,
        **kwargs,
    )


def create_planning_crew(
    tools_retriever=None,
    run_id=None,
    **kwargs,
):
    """
    Create a crew to plan the execution of a complex task, breaking it down
    into manageable components and identifying the optimal crew composition.

    Args:
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        run_id (str): The run id to use for the crew
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
        llm=create_reasoning_llm(run_id=run_id),
        run_id=run_id,
    )
    task = create_planning_task(
        agent=agent,
        tools=tools,
        run_id=run_id,
    )
    return create_default_crew(
        agents=[agent],
        tasks=[task],
        planning=True,
        planning_llm=create_reasoning_llm(run_id=run_id),
        run_id=run_id,
        **kwargs,
    )


def create_executing_crew(
    tools_retriever=None,
    plan=None,
    run_id=None,
    **kwargs,
):
    """
    Create a crew based on a pre-defined plan.

    Args:
        plan (PlanOutput): The plan to use for creating the crew
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        run_id (str): The run id to use for the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with agents and tasks from the plan
    """
    from crewai import Process
    from .llms import (
        create_default_llm,
        # create_reasoning_llm,
        create_chat_llm,
    )
    from .agents import create_default_agent
    from .tasks import create_default_task
    from .models import TaskPlan

    if not tools_retriever:
        raise ValueError("tools_retriever not provided")

    if not isinstance(plan, TaskPlan):
        raise ValueError("plan must be an instance of PlanOutput")

    # Create tasks based on the plan
    tasks = []
    tasks_agents = []
    for task in plan.tasks:
        task_tools = tools_retriever.get_batch(task.tools)
        task_tools = [t for t in task_tools if t is not None]
        task_agent = create_default_agent(
            role=task.agent_role,
            goal=task.agent_goal,
            backstory=task.agent_backstory,
            llm=create_default_llm(run_id=run_id),
            run_id=run_id,
        )
        tasks.append(
            create_default_task(
                agent=task_agent,
                name=task.name,
                description=task.description,
                expected_output=task.expected_output,
                human_input=task.requires_human,
                run_id=run_id,
                tools=task_tools or None,
            )
        )
        tasks_agents.append(task_agent)

    # Create and return the crew
    return create_default_crew(
        # manager_llm=create_reasoning_llm(run_id=run_id),
        chat_llm=create_chat_llm(run_id=run_id),
        tasks=tasks,
        agents=tasks_agents,
        process=Process.sequential,
        # memory=True,
        # planning=True,
        # planning_llm=create_reasoning_llm(run_id=run_id),
        run_id=run_id,
        **kwargs,
    )

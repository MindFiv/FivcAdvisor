from crewai import Crew


def create_simple_crew(*args, tools_retriever=None, tools_names=None, **kwargs):
    """
    Create a simple crew to handle a task with a single agent.

    Args:
        *args: Additional arguments to pass to Crew constructor
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        tools_names (List[str]): The names of the tools to use for the task
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with a single agent and task
    """
    from .llms import create_default_llm
    from .tasks import create_default_task
    from .agents import create_default_agent
    from .tools.retrievers import ToolsRetriever

    if not isinstance(tools_retriever, ToolsRetriever):
        raise ValueError("tool_retriever must be an instance of ToolsRetriever")

    if not isinstance(tools_names, list):
        raise ValueError("tool_names must be a list of strings")

    task_tools = tools_retriever.get_batch(tools_names)
    if None in task_tools:
        raise ValueError("Tools not found for simple task")

    agent = create_default_agent(llm=create_default_llm())
    task = create_default_task(
        agent=agent,
        tools=task_tools or None,
    )
    return Crew(agents=[agent], tasks=[task], **kwargs)


def create_tooling_crew(*args, tools_retriever=None, **kwargs):
    """
    Create a crew to retrieve tools for a task.

    Args:
        *args: Additional arguments to pass to Crew constructor
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with a tooling task
    """

    from .llms import create_reasoning_llm
    from .tasks import create_tooling_task
    from .agents import create_tooling_agent
    from .tools.retrievers import ToolsRetriever

    if not isinstance(tools_retriever, ToolsRetriever):
        raise ValueError("tool_retriever must be an instance of ToolsRetriever")

    agent = create_tooling_agent(llm=create_reasoning_llm())
    task = create_tooling_task(agent=agent, tools=[tools_retriever.to_tool()])
    return Crew(agents=[agent], tasks=[task], **kwargs)


def create_assessing_crew(*args, tools_retriever=None, **kwargs):
    """
    Create a crew to assess the complexity of a task and determine the best
    approach for handling it.

    Args:
        *args: Additional arguments to pass to Crew constructor
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with an assessment task
    """
    from .llms import create_reasoning_llm
    from .tasks import create_assessing_task
    from .agents import create_consulting_agent
    from .tools.retrievers import ToolsRetriever

    if not isinstance(tools_retriever, ToolsRetriever):
        raise ValueError("tool_retriever must be an instance of ToolsRetriever")

    agent = create_consulting_agent(llm=create_reasoning_llm())
    task = create_assessing_task(agent=agent, tools=[tools_retriever.to_tool()])
    return Crew(agents=[agent], tasks=[task], **kwargs)


def create_planning_crew(*args, tools_retriever=None, **kwargs):
    """
    Create a crew to plan the execution of a complex task, breaking it down
    into manageable components and identifying the optimal crew composition.

    Args:
        *args: Additional arguments to pass to Crew constructor
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
        **kwargs: Additional keyword arguments to pass to Crew constructor

    Returns:
        Crew: A configured crew with a planning task
    """
    from .llms import create_reasoning_llm
    from .tasks import create_planning_task
    from .agents import create_directing_agent
    from .tools.retrievers import ToolsRetriever

    if not isinstance(tools_retriever, ToolsRetriever):
        raise ValueError("tool_retriever must be an instance of ToolsRetriever")

    tools = [
        tools_retriever.get("sequentialthinking"),
        tools_retriever.to_tool(),
    ]
    tools = [t for t in tools if t is not None]
    agent = create_directing_agent(llm=create_reasoning_llm())
    task = create_planning_task(agent=agent, tools=tools)
    return Crew(
        agents=[agent],
        tasks=[task],
        planning=True,
        planning_llm=create_reasoning_llm(),
        **kwargs,
    )


def create_executing_crew(*args, tools_retriever=None, plan=None, **kwargs):
    """
    Create a crew based on a pre-defined plan.

    Args:
        *args: Additional arguments to pass to Crew constructor
        plan (PlanOutput): The plan to use for creating the crew
        tools_retriever (ToolsRetriever): The tool retriever to use for creating the crew
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
    from .agents import (
        create_default_agent,
    )
    from .tools.retrievers import ToolsRetriever
    from .tasks import create_default_task
    from .outputs import PlanOutput

    if not isinstance(tools_retriever, ToolsRetriever):
        raise ValueError("tool_retriever must be an instance of ToolsRetriever")

    if not isinstance(plan, PlanOutput):
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
                llm=create_default_llm(),
            )
        )

    # Create tasks based on the plan
    tasks = []
    for task_plan in plan.tasks:
        tasks.append(
            create_default_task(
                description=task_plan.description,
                expected_output=task_plan.expected_output,
            )
        )

    # Create and return the crew
    return Crew(
        manager_llm=create_reasoning_llm(),
        chat_llm=create_chat_llm(),
        tasks=tasks,
        agents=agents,
        process=Process.hierarchical,
        # memory=True,
        planning=True,
        planning_llm=create_reasoning_llm(),
        **kwargs,
    )

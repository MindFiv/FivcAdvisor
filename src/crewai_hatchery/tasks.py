from crewai import Task


def create_default_task(*args, **kwargs):
    """Create a default task for an agent."""
    if "agent" not in kwargs:
        from .llms import create_default_llm
        from .agents import create_default_agent

        kwargs["agent"] = create_default_agent(llm=create_default_llm())

    return Task(*args, **kwargs)


def create_assessing_task(*args, **kwargs):
    """Create an assessing task for an agent."""
    kwargs.setdefault(
        "description",
        """
        Analyze the user request and determine the best approach for handling it:
        
        User Request: "{user_query}"

        Your assessment should consider:
        1. Task complexity (simple, moderate, complex)
        2. Whether a single simple agent can handle this effectively
        3. What skills/capabilities are needed
        4. Whether this requires multiple specialized agents working together

        Provide your assessment in the specified format.
        """,
    )
    if "output_pydantic" not in kwargs:
        from .outputs import AssessmentOutput

        kwargs.update(
            expected_output="A structured assessment of the task complexity and recommended approach",
            output_pydantic=AssessmentOutput,
        )

    return create_default_task(*args, **kwargs)


def create_planning_task(*args, **kwargs):
    """Create a planning task for an agent."""
    kwargs.setdefault(
        "description",
        """
        Analyze the user request and create a plan for execution:
        
        User Request: "{user_query}"
        
        Your plan should:
        1. Break down the task into manageable sub tasks
        2. Identify what types of specialized agents are needed
        3. Specify the tools and resources required

        Then return the plan with agents and tasks in the specified format.
        """,
    )

    if "output_pydantic" not in kwargs:
        from .outputs import PlanningOutput

        kwargs.update(
            expected_output="A structured plan for executing the task",
            output_pydantic=PlanningOutput,
        )

    return create_default_task(*args, **kwargs)

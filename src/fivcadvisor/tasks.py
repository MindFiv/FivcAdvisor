__all__ = [
    "create_default_task",
    "create_tooling_task",
    "create_assessing_task",
    "create_planning_task",
]

from typing import Optional
from crewai import Task


class _Task(Task):
    session_id: Optional[str] = None


def create_default_task(*args, session_id=None, **kwargs):
    """Create a default task for an agent."""
    kwargs.setdefault(
        "description",
        """
        Execute the assigned task efficiently using available tools.
        User Request: {user_query}
        Make sure you are using the right tools.
        """,
    )
    if "output_pydantic" not in kwargs:
        from .models import QueryResponse

        kwargs.update(
            expected_output="A helpful, useful, and accurate response to the user query",
            output_pydantic=QueryResponse,
        )
    # kwargs.setdefault(
    #     "expected_output",
    #     """
    #     A helpful, useful, and accurate response to the user query.
    #     """,
    # )
    # if "agent" not in kwargs:
    #     from .llms import create_default_llm
    #     from .agents import create_default_agent
    #
    #     kwargs["agent"] = create_default_agent(llm=create_default_llm())

    task = _Task(*args, **kwargs)
    task.session_id = session_id
    return task


def create_tooling_task(*args, **kwargs):
    """
    Create a task for retrieving tools.
    """
    kwargs.setdefault(
        "description",
        """
        Retrieve the best tools for a given task.
        User Request: {user_query}
        """,
    )
    kwargs.setdefault(
        "expected_output",
        """
        A list of the best tools for the given task.
        """,
    )
    if "output_pydantic" not in kwargs:
        from .models import ToolRequirement

        kwargs.update(
            expected_output="A list of the best tools for the given task",
            output_pydantic=ToolRequirement,
        )

    return create_default_task(*args, **kwargs)


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
        from .models import TaskAssessment

        kwargs.update(
            expected_output="A structured assessment of the task complexity and recommended approach",
            output_pydantic=TaskAssessment,
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

        Then return the plan with agents and tasks in the specified format.
        """,
    )

    if "output_pydantic" not in kwargs:
        from .models import CrewPlan

        kwargs.update(
            expected_output="A structured plan for executing the task",
            output_pydantic=CrewPlan,
        )

    return create_default_task(*args, **kwargs)

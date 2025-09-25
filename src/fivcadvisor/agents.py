__all__ = [
    "create_default_agent",
    "create_tooling_agent",
    "create_consulting_agent",
    "create_directing_agent",
    "create_research_agent",
    "create_engineering_agent",
    "create_evaluating_agent",
]

from typing import Optional
from crewai import Agent


class _Agent(Agent):
    run_id: Optional[str] = None


def create_default_agent(*args, run_id=None, **kwargs):
    """Create a standard ReAct agent for task execution.

    Worker agents handle routine operational tasks and execute predefined
    workflows efficiently using the ReAct (Reasoning and Acting) pattern.
    """
    # Set default role if not provided
    kwargs.setdefault("role", "Generic Agent")
    kwargs.setdefault(
        "goal",
        """
        Execute assigned tasks efficiently 
        using available tools and predefined workflows.
        """,
    )
    kwargs.setdefault(
        "backstory",
        """
        A reliable task execution specialist 
        skilled in the ReAct pattern for reasoning and acting. 
        Expert at handling routine operational tasks, 
        following predefined workflows, 
        and efficiently utilizing available tools to 
        complete assignments with precision and consistency.
        """,
    )
    agent = _Agent(*args, **kwargs)
    agent.run_id = run_id
    return agent


def create_tooling_agent(*args, **kwargs):
    """Create an agent that can retrieve tools."""
    kwargs["role"] = "Tools Retriever"
    kwargs.setdefault(
        "goal",
        "Retrieve the best tools for a given task",
    )
    kwargs.setdefault(
        "backstory",
        "A tool retrieval specialist with deep expertise "
        "in identifying the most appropriate tools for a given task. "
        "Skilled at quickly assessing task requirements, "
        "analyzing available toolsets, and "
        "selecting the best tools for the job.",
    )
    return create_default_agent(*args, **kwargs)


def create_consulting_agent(*args, **kwargs):
    kwargs["role"] = "Consultant"
    kwargs.setdefault(
        "goal",
        "Assess task feasibility and execution decisions, "
        "determine if tasks can be handled by existing tools and flows, "
        "escalate complex requirements to Director agents, "
        "and optimize resource allocation",
    )
    kwargs.setdefault(
        "backstory",
        "A task feasibility and execution specialist "
        "with extensive experience in resource optimization and "
        "workflow assessment. "
        "Expert at quickly evaluating whether "
        "incoming tasks can be handled by existing tools and processes, "
        "or require new crew creation. "
        "Skilled at escalation decision-making, "
        "resource allocation optimization, "
        "and serving as the critical first point of "
        "assessment in the system workflow.",
    )
    return create_default_agent(*args, **kwargs)


def create_directing_agent(*args, **kwargs):
    kwargs.update(
        role="Director",
        memory=True,
        reasoning=True,
        allow_delegation=True,
    )
    kwargs.setdefault(
        "goal",
        "Design and assemble specialized crews for complex task execution, "
        "break down complex tasks into manageable components, "
        "and coordinate multi-agent workflows with strategic orchestration",
    )
    kwargs.setdefault(
        "backstory",
        "A strategic orchestration specialist with extensive experience "
        "in team building and workflow design. "
        "Expert at analyzing complex requirements, "
        "identifying optimal crew compositions, "
        "and coordinating multi-agent systems. "
        "Skilled in dynamic scaling of worker teams and "
        "real-time performance monitoring with the ability to "
        "make strategic adjustments on the fly.",
    )
    return create_default_agent(*args, **kwargs)


def create_research_agent(*args, **kwargs):
    kwargs["role"] = "Researcher"
    kwargs.setdefault(
        "goal",
        "Identify common workflow patterns, "
        "analyze task flows within specific domains, "
        "and generate insights for system optimization through "
        "comprehensive pattern recognition and domain analysis",
    )
    kwargs.setdefault(
        "backstory",
        "A pattern recognition specialist and domain analysis expert "
        "with deep expertise in workflow optimization. "
        "Skilled at identifying recurring task sequences, "
        "analyzing execution patterns across different domains, "
        "and extracting actionable insights from complex data flows. "
        "Experienced in comprehensive logging analysis and "
        "workflow pattern summarization to "
        "drive continuous system improvement.",
    )
    return create_default_agent(*args, **kwargs)


def create_engineering_agent(*args, **kwargs):
    kwargs.update(
        role="Engineer",
        allow_code_execution=True,
    )
    kwargs.setdefault(
        "goal",
        "Create new tools based on identified needs, "
        "maintain and optimize existing toolsets, "
        "and implement system improvements through "
        "autonomous tool development and code generation",
    )
    kwargs.setdefault(
        "backstory",
        "A tool development specialist and code generation expert "
        "with extensive experience in creating composite tools from "
        "existing components. "
        "Skilled at autonomous tool creation, "
        "combining multiple functionalities into cohesive solutions, "
        "and implementing self-improving systems based on usage patterns. "
        "Expert in maintaining toolset ecosystems and "
        "optimizing tool performance for maximum efficiency.",
    )
    return create_default_agent(*args, **kwargs)


def create_evaluating_agent(*args, **kwargs):
    kwargs["role"] = "Evaluator"
    kwargs.setdefault(
        "goal",
        "Monitor tool and agent performance, "
        "provide feedback for continuous improvement, "
        "validate new tool effectiveness, "
        "and identify classification opportunities "
        "for decision optimization",
    )
    kwargs.setdefault(
        "backstory",
        "A performance assessment specialist and "
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

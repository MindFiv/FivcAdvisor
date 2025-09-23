from typing import List
from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    """Description for a query response."""

    answer: str = Field(description="Response to the user query")
    reasoning: str = Field(description="Reasoning behind the answer")


class TaskAssessment(BaseModel):
    """Description for an assessment result for a task."""

    task_complexity: str = Field(description="Simple, moderate, or complex")
    require_director: bool = Field(
        description="Whether we need a director to handle this task "
        "instead of a default agent"
    )
    required_tools: List[str] = Field(
        description="List of skills/tools needed "
        "if we are about to use a default agent"
    )
    answer: str = Field(
        description="Answer to the user query if task is simple "
        "and no tools are required"
    )
    reasoning: str = Field(description="Explanation of the assessment")


class ToolRequirement(BaseModel):
    """Description for a tool result for a task."""

    tools: List[str] = Field(description="List of tools needed for the task")


class CrewPlan(BaseModel):
    """Description for a plan for a task."""

    class Agent(BaseModel):
        """Description for a planning agent."""

        role: str = Field(description="Role of the agent")
        goal: str = Field(description="Goal of the agent")
        backstory: str = Field(description="Backstory of the agent")
        tools: List[str] = Field(description="List of tools needed for the agent")

    class Task(BaseModel):
        """Description for a planning task."""

        name: str = Field(description="Name of the task")
        description: str = Field(description="Description of the task")
        expected_output: str = Field(description="Expected output of the task")
        tools: List[str] = Field(
            description="List of tools needed for the task, "
            "if different from the agent's default tools"
        )
        requires_human: bool = Field(
            description="Whether human input is required for this agent"
        )
        # agent_role: str = Field(description="Role of the agent for this task")

    agents: List[Agent] = Field(description="List of agents needed for the task")
    tasks: List[Task] = Field(description="List of tasks to be executed")

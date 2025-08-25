from typing import List
from pydantic import BaseModel, Field


class AssessmentOutput(BaseModel):
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
    reasoning: str = Field(description="Explanation of the assessment")


class ToolOutput(BaseModel):
    """Description for a tool result for a task."""

    tools: List[str] = Field(description="List of tools needed for the task")


class PlanOutput(BaseModel):
    """Description for a plan for a task."""

    class Agent(BaseModel):
        """Description for a planning agent."""

        role: str = Field(description="Role of the agent")
        goal: str = Field(description="Goal of the agent")
        backstory: str = Field(description="Backstory of the agent")
        tools: List[str] = Field(description="List of tools needed for the agent")

    class Task(BaseModel):
        """Description for a planning task."""

        description: str = Field(description="Description of the task")
        expected_output: str = Field(description="Expected output of the task")
        # tools: List[str] = Field(
        #     description="List of tools needed for the task, "
        #     "excluding Tools Retriever"
        # )
        # agent_role: str = Field(description="Role of the agent for this task")

    agents: List[Agent] = Field(description="List of agents needed for the task")
    tasks: List[Task] = Field(description="List of tasks to be executed")

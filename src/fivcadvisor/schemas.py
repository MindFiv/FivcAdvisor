from typing import List
from pydantic import BaseModel, Field


class TaskAssessment(BaseModel):
    """Description for an assessment result for a task."""

    require_planning: bool = Field(
        description="Whether a planning agent is required to break down the task"
    )
    require_tools: List[str] = Field(
        description="List of tools needed for the task, if we can't answer directly"
    )
    answer: str = Field(
        description="Answer to the user query directly if task is simple and no tools are required"
    )


class TaskRequirement(BaseModel):
    """Description for a requirement for a task."""

    tools: List[str] = Field(description="List of tools needed for the task")


class TaskTeam(BaseModel):
    """Description for a plan for a task."""

    class Specialist(BaseModel):
        """Description for a planning task."""

        name: str = Field(description="Name of the agent for this task")
        backstory: str = Field(description="Backstory for the agent")
        tools: List[str] = Field(description="List of tools needed for the agent")

    specialists: List[Specialist] = Field(
        description="List of agents needed for the task"
    )

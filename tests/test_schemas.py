#!/usr/bin/env python3
"""
Tests for the schemas module.
"""

import pytest
from pydantic import ValidationError

from fivcadvisor.schemas import (
    TaskAssessment,
    TaskRequirement,
    TaskTeam,
)


class TestTaskAssessment:
    """Test the TaskAssessment schema."""

    def test_init_basic(self):
        """Test basic TaskAssessment initialization."""
        assessment = TaskAssessment(
            require_planning=True,
            require_tools=["calculator", "python_repl"],
            answer="This is a complex task",
        )

        assert assessment.require_planning is True
        assert assessment.require_tools == ["calculator", "python_repl"]
        assert assessment.answer == "This is a complex task"

    def test_init_no_tools(self):
        """Test TaskAssessment with no tools required."""
        assessment = TaskAssessment(
            require_planning=False,
            require_tools=[],
            answer="Simple answer",
        )

        assert assessment.require_planning is False
        assert assessment.require_tools == []
        assert assessment.answer == "Simple answer"

    def test_validation_error(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskAssessment(require_planning=True)

    def test_dict_conversion(self):
        """Test conversion to dictionary."""
        assessment = TaskAssessment(
            require_planning=True,
            require_tools=["tool1"],
            answer="answer",
        )
        data = assessment.model_dump()

        assert data["require_planning"] is True
        assert data["require_tools"] == ["tool1"]
        assert data["answer"] == "answer"

    def test_json_schema(self):
        """Test JSON schema generation."""
        schema = TaskAssessment.model_json_schema()

        assert "properties" in schema
        assert "require_planning" in schema["properties"]
        assert "require_tools" in schema["properties"]
        assert "answer" in schema["properties"]


class TestTaskRequirement:
    """Test the TaskRequirement schema."""

    def test_init_basic(self):
        """Test basic TaskRequirement initialization."""
        requirement = TaskRequirement(
            tools=["calculator", "python_repl", "current_time"]
        )

        assert requirement.tools == ["calculator", "python_repl", "current_time"]

    def test_init_empty_tools(self):
        """Test TaskRequirement with empty tools list."""
        requirement = TaskRequirement(tools=[])

        assert requirement.tools == []

    def test_validation_error(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskRequirement()

    def test_dict_conversion(self):
        """Test conversion to dictionary."""
        requirement = TaskRequirement(tools=["tool1", "tool2"])
        data = requirement.model_dump()

        assert data["tools"] == ["tool1", "tool2"]

    def test_json_schema(self):
        """Test JSON schema generation."""
        schema = TaskRequirement.model_json_schema()

        assert "properties" in schema
        assert "tools" in schema["properties"]


class TestTaskTeam:
    """Test the TaskTeam schema."""

    def test_specialist_init(self):
        """Test Specialist initialization."""
        specialist = TaskTeam.Specialist(
            name="Research Agent",
            backstory="An expert researcher",
            tools=["search", "summarize"],
        )

        assert specialist.name == "Research Agent"
        assert specialist.backstory == "An expert researcher"
        assert specialist.tools == ["search", "summarize"]

    def test_task_team_init(self):
        """Test TaskTeam initialization."""
        specialist1 = TaskTeam.Specialist(
            name="Agent1", backstory="Backstory1", tools=["tool1"]
        )
        specialist2 = TaskTeam.Specialist(
            name="Agent2", backstory="Backstory2", tools=["tool2"]
        )

        team = TaskTeam(specialists=[specialist1, specialist2])

        assert len(team.specialists) == 2
        assert team.specialists[0].name == "Agent1"
        assert team.specialists[1].name == "Agent2"

    def test_task_team_empty(self):
        """Test TaskTeam with empty specialists list."""
        team = TaskTeam(specialists=[])

        assert team.specialists == []

    def test_validation_error(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskTeam()

    def test_specialist_validation_error(self):
        """Test that Specialist with missing fields raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskTeam.Specialist(name="Agent1")

    def test_dict_conversion(self):
        """Test conversion to dictionary."""
        specialist = TaskTeam.Specialist(
            name="Agent", backstory="Story", tools=["tool"]
        )
        team = TaskTeam(specialists=[specialist])
        data = team.model_dump()

        assert "specialists" in data
        assert len(data["specialists"]) == 1
        assert data["specialists"][0]["name"] == "Agent"
        assert data["specialists"][0]["backstory"] == "Story"
        assert data["specialists"][0]["tools"] == ["tool"]

    def test_json_schema(self):
        """Test JSON schema generation."""
        schema = TaskTeam.model_json_schema()

        assert "properties" in schema
        assert "specialists" in schema["properties"]

    def test_nested_specialist_schema(self):
        """Test that Specialist schema is properly nested."""
        schema = TaskTeam.model_json_schema()

        # Check that Specialist is defined in the schema
        assert "$defs" in schema or "definitions" in schema


if __name__ == "__main__":
    pytest.main([__file__])

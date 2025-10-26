#!/usr/bin/env python3
"""
Comprehensive tests for task creation functions.

Tests verify:
- create_tooling_task functionality
- create_briefing_task functionality
- create_assessing_task functionality
- create_planning_task functionality
- Query prepending and formatting
- Response format configuration
- Tools retriever integration
- Runnable interface compliance
"""

from unittest.mock import MagicMock, patch

from fivcadvisor.tasks import (
    create_tooling_task,
    create_briefing_task,
    create_assessing_task,
    create_planning_task,
)
from fivcadvisor.tasks.types import TaskRunnable
from fivcadvisor.tasks.types.base import (
    TaskAssessment,
    TaskRequirement,
    TaskTeam,
)
from fivcadvisor.utils import Runnable


class TestCreateToolingTask:
    """Test create_tooling_task function."""

    @patch("fivcadvisor.tasks.agents.create_tooling_agent")
    def test_create_tooling_task_basic(self, mock_create_agent):
        """Test basic create_tooling_task."""
        mock_agent = MagicMock(spec=Runnable)
        mock_agent.id.return_value = "agent-123"
        mock_create_agent.return_value = mock_agent

        task = create_tooling_task("Find tools for data analysis")

        assert isinstance(task, TaskRunnable)
        assert "Retrieve the best tools" in task._query
        assert "Find tools for data analysis" in task._query

    @patch("fivcadvisor.tasks.agents.create_tooling_agent")
    def test_create_tooling_task_sets_response_format(self, mock_create_agent):
        """Test that create_tooling_task sets response_format to TaskRequirement."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        create_tooling_task("Test query")

        # Verify response_format was set
        call_kwargs = mock_create_agent.call_args[1]
        assert call_kwargs.get("response_format") == TaskRequirement

    @patch("fivcadvisor.tasks.agents.create_tooling_agent")
    def test_create_tooling_task_with_tools_retriever(self, mock_create_agent):
        """Test create_tooling_task with tools_retriever."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        mock_retriever = MagicMock()
        mock_tool = MagicMock()
        mock_retriever.to_tool.return_value = mock_tool

        create_tooling_task("Test query", tools_retriever=mock_retriever)

        # Verify tools were added
        call_kwargs = mock_create_agent.call_args[1]
        assert "tools" in call_kwargs
        assert mock_tool in call_kwargs["tools"]

    @patch("fivcadvisor.tasks.agents.create_tooling_agent")
    def test_create_tooling_task_with_kwargs(self, mock_create_agent):
        """Test create_tooling_task with additional kwargs."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        create_tooling_task("Test query", model="gpt-4", temperature=0.5)

        call_kwargs = mock_create_agent.call_args[1]
        assert call_kwargs.get("model") == "gpt-4"
        assert call_kwargs.get("temperature") == 0.5


class TestCreateBriefingTask:
    """Test create_briefing_task function."""

    @patch("fivcadvisor.tasks.agents.create_consultant_agent")
    def test_create_briefing_task_basic(self, mock_create_agent):
        """Test basic create_briefing_task."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        task = create_briefing_task("Long content to summarize")

        assert isinstance(task, TaskRunnable)
        assert "Summarize the following content" in task._query
        assert "Long content to summarize" in task._query

    @patch("fivcadvisor.tasks.agents.create_consultant_agent")
    def test_create_briefing_task_with_tools_retriever(self, mock_create_agent):
        """Test create_briefing_task with tools_retriever."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        mock_retriever = MagicMock()
        mock_tool = MagicMock()
        mock_retriever.to_tool.return_value = mock_tool

        create_briefing_task("Test content", tools_retriever=mock_retriever)

        call_kwargs = mock_create_agent.call_args[1]
        assert "tools" in call_kwargs
        assert mock_tool in call_kwargs["tools"]

    @patch("fivcadvisor.tasks.agents.create_consultant_agent")
    def test_create_briefing_task_with_kwargs(self, mock_create_agent):
        """Test create_briefing_task with additional kwargs."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        create_briefing_task("Test content", max_tokens=100)

        call_kwargs = mock_create_agent.call_args[1]
        assert call_kwargs.get("max_tokens") == 100


class TestCreateAssessingTask:
    """Test create_assessing_task function."""

    @patch("fivcadvisor.tasks.agents.create_consultant_agent")
    def test_create_assessing_task_basic(self, mock_create_agent):
        """Test basic create_assessing_task."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        task = create_assessing_task("Is this complex?")

        assert isinstance(task, TaskRunnable)
        assert "Assess the following query" in task._query
        assert "Is this complex?" in task._query

    @patch("fivcadvisor.tasks.agents.create_consultant_agent")
    def test_create_assessing_task_sets_response_format(self, mock_create_agent):
        """Test that create_assessing_task sets response_format to TaskAssessment."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        create_assessing_task("Test query")

        call_kwargs = mock_create_agent.call_args[1]
        assert call_kwargs.get("response_format") == TaskAssessment

    @patch("fivcadvisor.tasks.agents.create_consultant_agent")
    def test_create_assessing_task_includes_planning_guidance(self, mock_create_agent):
        """Test that create_assessing_task includes planning guidance in query."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        task = create_assessing_task("Test query")

        assert "require_planning" in task._query
        assert "reasoning" in task._query

    @patch("fivcadvisor.tasks.agents.create_consultant_agent")
    def test_create_assessing_task_with_tools_retriever(self, mock_create_agent):
        """Test create_assessing_task with tools_retriever."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        mock_retriever = MagicMock()
        mock_tool = MagicMock()
        mock_retriever.to_tool.return_value = mock_tool

        create_assessing_task("Test query", tools_retriever=mock_retriever)

        call_kwargs = mock_create_agent.call_args[1]
        assert "tools" in call_kwargs


class TestCreatePlanningTask:
    """Test create_planning_task function."""

    @patch("fivcadvisor.tasks.agents.create_planning_agent")
    def test_create_planning_task_basic(self, mock_create_agent):
        """Test basic create_planning_task."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        task = create_planning_task("Plan this complex task")

        assert isinstance(task, TaskRunnable)
        assert "Plan the following query" in task._query
        assert "Plan this complex task" in task._query

    @patch("fivcadvisor.tasks.agents.create_planning_agent")
    def test_create_planning_task_sets_response_format(self, mock_create_agent):
        """Test that create_planning_task sets response_format to TaskTeam."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        create_planning_task("Test query")

        call_kwargs = mock_create_agent.call_args[1]
        assert call_kwargs.get("response_format") == TaskTeam

    @patch("fivcadvisor.tasks.agents.create_planning_agent")
    def test_create_planning_task_includes_specialist_guidance(self, mock_create_agent):
        """Test that create_planning_task includes specialist guidance in query."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        task = create_planning_task("Test query")

        assert "specialists" in task._query
        assert "name" in task._query
        assert "backstory" in task._query
        assert "tools" in task._query

    @patch("fivcadvisor.tasks.agents.create_planning_agent")
    def test_create_planning_task_with_tools_retriever(self, mock_create_agent):
        """Test create_planning_task with tools_retriever."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        mock_retriever = MagicMock()
        mock_tool = MagicMock()
        mock_retriever.to_tool.return_value = mock_tool

        create_planning_task("Test query", tools_retriever=mock_retriever)

        call_kwargs = mock_create_agent.call_args[1]
        assert "tools" in call_kwargs

    @patch("fivcadvisor.tasks.agents.create_planning_agent")
    def test_create_planning_task_with_kwargs(self, mock_create_agent):
        """Test create_planning_task with additional kwargs."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        create_planning_task("Test query", temperature=0.7)

        call_kwargs = mock_create_agent.call_args[1]
        assert call_kwargs.get("temperature") == 0.7


class TestTaskCreationIntegration:
    """Integration tests for task creation functions."""

    @patch("fivcadvisor.tasks.agents.create_tooling_agent")
    @patch("fivcadvisor.tasks.agents.create_consultant_agent")
    @patch("fivcadvisor.tasks.agents.create_planning_agent")
    def test_all_task_types_return_runnable(
        self, mock_planning, mock_consultant, mock_tooling
    ):
        """Test that all task creation functions return Runnable instances."""
        mock_agent = MagicMock(spec=Runnable)
        mock_tooling.return_value = mock_agent
        mock_consultant.return_value = mock_agent
        mock_planning.return_value = mock_agent

        tooling = create_tooling_task("Test")
        briefing = create_briefing_task("Test")
        assessing = create_assessing_task("Test")
        planning = create_planning_task("Test")

        assert isinstance(tooling, TaskRunnable)
        assert isinstance(briefing, TaskRunnable)
        assert isinstance(assessing, TaskRunnable)
        assert isinstance(planning, TaskRunnable)

    @patch("fivcadvisor.tasks.agents.create_tooling_agent")
    def test_task_creation_with_empty_query(self, mock_create_agent):
        """Test task creation with empty query."""
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        task = create_tooling_task("")

        assert isinstance(task, TaskRunnable)
        assert task._query is not None

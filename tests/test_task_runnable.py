#!/usr/bin/env python3
"""
Comprehensive tests for TaskRunnable implementation.

Tests verify:
- TaskRunnable initialization with query and runnable
- Synchronous execution via run() method
- Asynchronous execution via run_async() method
- Query prepending to underlying runnable
- ID delegation to underlying runnable
- Error handling and edge cases
- Runnable interface compliance
- Response parsing with response_format parameter
- JSON string to Pydantic model conversion
"""

import json
import pytest
from pydantic import BaseModel

from fivcadvisor.tasks.types import TaskRunnable
from fivcadvisor.tasks.types.base import TaskAssessment, TaskRequirement, TaskTeam
from fivcadvisor.utils import Runnable


class MockRunnable(Runnable):
    """Mock runnable for testing TaskRunnable."""

    def __init__(self, runnable_id: str = "mock-runnable-123"):
        self._id = runnable_id
        self.last_query = None
        self.last_kwargs = None

    def id(self) -> str:
        return self._id

    def run(self, query: str, **kwargs) -> BaseModel:
        """Mock run method that captures query and kwargs."""
        self.last_query = query
        self.last_kwargs = kwargs
        return TaskAssessment(require_planning=True, reasoning="Mock response")

    async def run_async(self, query: str, **kwargs) -> BaseModel:
        """Mock async run method that captures query and kwargs."""
        self.last_query = query
        self.last_kwargs = kwargs
        return TaskAssessment(require_planning=False, reasoning="Mock async response")


class StringReturningMockRunnable(Runnable):
    """Mock runnable that returns JSON strings instead of BaseModel instances."""

    def __init__(
        self, runnable_id: str = "string-mock-123", response_data: dict = None
    ):
        self._id = runnable_id
        self.response_data = response_data or {
            "require_planning": True,
            "reasoning": "Test reasoning",
        }
        self.last_query = None
        self.last_kwargs = None

    def id(self) -> str:
        return self._id

    def run(self, query: str, **kwargs) -> str:
        """Mock run method that returns JSON string."""
        self.last_query = query
        self.last_kwargs = kwargs
        return json.dumps(self.response_data)

    async def run_async(self, query: str, **kwargs) -> str:
        """Mock async run method that returns JSON string."""
        self.last_query = query
        self.last_kwargs = kwargs
        return json.dumps(self.response_data)


class TestTaskRunnableInitialization:
    """Test TaskRunnable initialization."""

    def test_init_basic(self):
        """Test basic TaskRunnable initialization."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test query", runnable=mock_runnable)

        assert task._query == "Test query"
        assert task._runnable == mock_runnable

    def test_init_with_empty_query(self):
        """Test TaskRunnable initialization with empty query."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="", runnable=mock_runnable)

        assert task._query == ""
        assert task._runnable == mock_runnable

    def test_init_with_long_query(self):
        """Test TaskRunnable initialization with long query."""
        mock_runnable = MockRunnable()
        long_query = "x" * 10000
        task = TaskRunnable(query=long_query, runnable=mock_runnable)

        assert task._query == long_query
        assert len(task._query) == 10000

    def test_init_with_special_characters(self):
        """Test TaskRunnable initialization with special characters."""
        mock_runnable = MockRunnable()
        special_query = "Test query with special chars: !@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        task = TaskRunnable(query=special_query, runnable=mock_runnable)

        assert task._query == special_query

    def test_init_with_multiline_query(self):
        """Test TaskRunnable initialization with multiline query."""
        mock_runnable = MockRunnable()
        multiline_query = "Line 1\nLine 2\nLine 3"
        task = TaskRunnable(query=multiline_query, runnable=mock_runnable)

        assert task._query == multiline_query


class TestTaskRunnableID:
    """Test TaskRunnable ID delegation."""

    def test_id_delegation(self):
        """Test that id() delegates to underlying runnable."""
        mock_runnable = MockRunnable(runnable_id="test-id-456")
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        assert task.id() == "test-id-456"

    def test_id_consistency(self):
        """Test that id() returns consistent value."""
        mock_runnable = MockRunnable(runnable_id="consistent-id")
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        id1 = task.id()
        id2 = task.id()
        assert id1 == id2 == "consistent-id"

    def test_id_with_different_runnables(self):
        """Test id() with different underlying runnables."""
        runnable1 = MockRunnable(runnable_id="id-1")
        runnable2 = MockRunnable(runnable_id="id-2")

        task1 = TaskRunnable(query="Test", runnable=runnable1)
        task2 = TaskRunnable(query="Test", runnable=runnable2)

        assert task1.id() == "id-1"
        assert task2.id() == "id-2"


class TestTaskRunnableRun:
    """Test TaskRunnable synchronous execution."""

    def test_run_basic(self):
        """Test basic run() execution."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test query", runnable=mock_runnable)

        result = task.run()

        assert isinstance(result, TaskAssessment)
        assert mock_runnable.last_query == "Test query"

    def test_run_prepends_query(self):
        """Test that run() prepends the task query."""
        mock_runnable = MockRunnable()
        task_query = "Task-specific query"
        task = TaskRunnable(query=task_query, runnable=mock_runnable)

        task.run()

        assert mock_runnable.last_query == task_query

    def test_run_with_kwargs(self):
        """Test run() with additional keyword arguments."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        task.run(extra_param="value", another_param=123)

        assert mock_runnable.last_kwargs == {
            "extra_param": "value",
            "another_param": 123,
        }

    def test_run_returns_basemodel(self):
        """Test that run() returns a BaseModel instance."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        result = task.run()

        assert isinstance(result, BaseModel)

    def test_run_multiple_times(self):
        """Test calling run() multiple times."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        result1 = task.run()
        result2 = task.run()

        assert isinstance(result1, TaskAssessment)
        assert isinstance(result2, TaskAssessment)
        assert mock_runnable.last_query == "Test"


class TestTaskRunnableRunAsync:
    """Test TaskRunnable asynchronous execution."""

    @pytest.mark.asyncio
    async def test_run_async_basic(self):
        """Test basic run_async() execution."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test query", runnable=mock_runnable)

        result = await task.run_async()

        assert isinstance(result, TaskAssessment)
        assert mock_runnable.last_query == "Test query"

    @pytest.mark.asyncio
    async def test_run_async_prepends_query(self):
        """Test that run_async() prepends the task query."""
        mock_runnable = MockRunnable()
        task_query = "Async task query"
        task = TaskRunnable(query=task_query, runnable=mock_runnable)

        await task.run_async()

        assert mock_runnable.last_query == task_query

    @pytest.mark.asyncio
    async def test_run_async_with_kwargs(self):
        """Test run_async() with additional keyword arguments."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        await task.run_async(param1="value1", param2=456)

        assert mock_runnable.last_kwargs == {"param1": "value1", "param2": 456}

    @pytest.mark.asyncio
    async def test_run_async_returns_basemodel(self):
        """Test that run_async() returns a BaseModel instance."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        result = await task.run_async()

        assert isinstance(result, BaseModel)

    @pytest.mark.asyncio
    async def test_run_async_multiple_times(self):
        """Test calling run_async() multiple times."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        result1 = await task.run_async()
        result2 = await task.run_async()

        assert isinstance(result1, TaskAssessment)
        assert isinstance(result2, TaskAssessment)


class TestTaskRunnableIntegration:
    """Integration tests for TaskRunnable."""

    def test_run_and_run_async_consistency(self):
        """Test that run() and run_async() behave consistently."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        result_sync = task.run()
        assert isinstance(result_sync, TaskAssessment)

    def test_task_runnable_with_different_response_types(self):
        """Test TaskRunnable with different response types."""

        class CustomMockRunnable(Runnable):
            def __init__(self, response_type):
                self.response_type = response_type

            def id(self) -> str:
                return "custom-mock"

            def run(self, query: str, **kwargs) -> BaseModel:
                if self.response_type == "assessment":
                    return TaskAssessment(require_planning=True)
                elif self.response_type == "requirement":
                    return TaskRequirement(tools=["tool1", "tool2"])
                elif self.response_type == "team":
                    return TaskTeam(specialists=[])
                return TaskAssessment(require_planning=False)

            async def run_async(self, query: str, **kwargs) -> BaseModel:
                return self.run(query, **kwargs)

        # Test with different response types
        for response_type in ["assessment", "requirement", "team"]:
            mock_runnable = CustomMockRunnable(response_type)
            task = TaskRunnable(query="Test", runnable=mock_runnable)
            result = task.run()
            assert isinstance(result, BaseModel)


class TestTaskRunnableResponseParsing:
    """Test TaskRunnable response parsing with response_format parameter."""

    def test_parse_response_with_json_string_assessment(self):
        """Test parsing JSON string to TaskAssessment."""
        response_data = {
            "require_planning": True,
            "reasoning": "This is a complex task",
        }
        mock_runnable = StringReturningMockRunnable(response_data=response_data)
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskAssessment
        )

        result = task.run()

        assert isinstance(result, TaskAssessment)
        assert result.require_planning is True
        assert result.reasoning == "This is a complex task"

    def test_parse_response_with_json_string_requirement(self):
        """Test parsing JSON string to TaskRequirement."""
        response_data = {"tools": ["tool1", "tool2", "tool3"]}
        mock_runnable = StringReturningMockRunnable(response_data=response_data)
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskRequirement
        )

        result = task.run()

        assert isinstance(result, TaskRequirement)
        assert result.tools == ["tool1", "tool2", "tool3"]

    @pytest.mark.asyncio
    async def test_parse_response_async_with_json_string(self):
        """Test async parsing of JSON string to TaskAssessment."""
        response_data = {"require_planning": False, "reasoning": "Simple task"}
        mock_runnable = StringReturningMockRunnable(response_data=response_data)
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskAssessment
        )

        result = await task.run_async()

        assert isinstance(result, TaskAssessment)
        assert result.require_planning is False
        assert result.reasoning == "Simple task"

    def test_parse_response_without_response_format(self):
        """Test that response is returned as-is when no response_format is set."""
        mock_runnable = StringReturningMockRunnable()
        task = TaskRunnable(query="Test", runnable=mock_runnable)

        result = task.run()

        # Should return the JSON string as-is
        assert isinstance(result, str)
        assert "require_planning" in result

    def test_parse_response_with_basemodel_instance(self):
        """Test that BaseModel instances are returned as-is."""
        mock_runnable = MockRunnable()
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskAssessment
        )

        result = task.run()

        # Should return the BaseModel instance as-is
        assert isinstance(result, TaskAssessment)
        assert result.require_planning is True

    def test_parse_response_with_json_embedded_in_text(self):
        """Test parsing JSON embedded in text response."""

        class EmbeddedJsonMockRunnable(Runnable):
            def id(self) -> str:
                return "embedded-mock"

            def run(self, query: str, **kwargs) -> str:
                return 'Here is the assessment: {"require_planning": true, "reasoning": "Complex"}'

            async def run_async(self, query: str, **kwargs) -> str:
                return self.run(query, **kwargs)

        mock_runnable = EmbeddedJsonMockRunnable()
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskAssessment
        )

        result = task.run()

        assert isinstance(result, TaskAssessment)
        assert result.require_planning is True
        assert result.reasoning == "Complex"

    def test_parse_response_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError."""

        class InvalidJsonMockRunnable(Runnable):
            def id(self) -> str:
                return "invalid-mock"

            def run(self, query: str, **kwargs) -> str:
                return "This is not valid JSON at all"

            async def run_async(self, query: str, **kwargs) -> str:
                return self.run(query, **kwargs)

        mock_runnable = InvalidJsonMockRunnable()
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskAssessment
        )

        with pytest.raises(ValueError):
            task.run()

    def test_parse_response_with_multiple_models(self):
        """Test parsing with different response formats."""
        # Test with TaskAssessment
        assessment_data = {"require_planning": True, "reasoning": "Test"}
        mock_runnable = StringReturningMockRunnable(response_data=assessment_data)
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskAssessment
        )
        result = task.run()
        assert isinstance(result, TaskAssessment)

        # Test with TaskRequirement
        requirement_data = {"tools": ["tool1"]}
        mock_runnable = StringReturningMockRunnable(response_data=requirement_data)
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskRequirement
        )
        result = task.run()
        assert isinstance(result, TaskRequirement)

    @pytest.mark.asyncio
    async def test_parse_response_async_consistency(self):
        """Test that async parsing is consistent with sync parsing."""
        response_data = {"require_planning": True, "reasoning": "Consistent test"}
        mock_runnable = StringReturningMockRunnable(response_data=response_data)
        task = TaskRunnable(
            query="Test", runnable=mock_runnable, response_format=TaskAssessment
        )

        result_sync = task.run()
        result_async = await task.run_async()

        assert isinstance(result_sync, TaskAssessment)
        assert isinstance(result_async, TaskAssessment)
        assert result_sync.require_planning == result_async.require_planning
        assert result_sync.reasoning == result_async.reasoning

"""
Task Runnable wrapper for agent execution.

This module provides TaskRunnable, a wrapper around agent runnables that
prepends a task-specific query to the execution context.

Key Components:
    - TaskRunnable: Wraps an agent runnable with a task query
"""

import json
from typing import Any, Optional, Type

from pydantic import BaseModel

from fivcadvisor.utils import Runnable


class TaskRunnable(Runnable):
    """
    Wrapper for task-specific agent execution.

    TaskRunnable wraps an agent runnable and prepends a task-specific query
    to the execution. This is useful for creating specialized tasks like
    tooling, briefing, assessing, and planning tasks.

    The wrapper delegates all execution to the underlying runnable while
    automatically injecting the task query as the first argument.

    Attributes:
        _query: The task-specific query to prepend to execution
        _runnable: The underlying agent runnable to execute

    Example:
        >>> from fivcadvisor.tasks import create_tooling_task
        >>> task = create_tooling_task("Find tools for data analysis")
        >>> result = task.run()  # Executes with prepended query
    """

    def __init__(
        self,
        query: str,
        runnable: Runnable,
        response_format: Optional[Type[BaseModel]] = None,
        **kwargs,
    ):
        """
        Initialize TaskRunnable with a query and underlying runnable.

        Args:
            query: The task-specific query to prepend to execution.
                   This query will be passed as the first argument to the
                   underlying runnable's run/run_async methods.
            runnable: The underlying agent runnable to wrap and execute.
                     Must implement the Runnable interface with run() and
                     run_async() methods.
            response_format: Optional Pydantic model class to parse the response into.
                           If provided, the string response will be parsed as JSON
                           and converted to this model type.
            **kwargs: Additional keyword arguments (reserved for future use).

        Raises:
            TypeError: If runnable does not implement the Runnable interface.
        """
        self._query = query
        self._runnable = runnable
        self._response_format = response_format

    @property
    def id(self) -> str:
        """
        Get the unique identifier for this runnable.

        Returns the ID of the underlying runnable, ensuring consistent
        identification across the task execution pipeline.

        Returns:
            str: The unique identifier of the underlying runnable.
        """
        return self._runnable.id

    def run(self, **kwargs: Any) -> BaseModel:
        """
        Execute the task synchronously.

        Prepends the task query to the execution and delegates to the
        underlying runnable's run method. The query is passed as the
        first positional argument.

        Args:
            **kwargs: Additional keyword arguments to pass to the underlying
                     runnable's run method.

        Returns:
            BaseModel: The execution result from the underlying runnable,
                      typically a Pydantic model instance (e.g., TaskAssessment,
                      TaskRequirement, TaskTeam).

        Raises:
            Exception: Any exception raised by the underlying runnable.

        Example:
            >>> task = create_assessing_task("Is this complex?")
            >>> result = task.run()  # Returns TaskAssessment
            >>> print(result.require_planning)
        """
        result = self._runnable.run(self._query, **kwargs)
        return self._parse_response(result)

    async def run_async(self, **kwargs: Any) -> BaseModel:
        """
        Execute the task asynchronously.

        Prepends the task query to the execution and delegates to the
        underlying runnable's run_async method. The query is passed as the
        first positional argument.

        This method is useful for non-blocking execution in async contexts,
        such as web servers or concurrent task processing.

        Args:
            **kwargs: Additional keyword arguments to pass to the underlying
                     runnable's run_async method.

        Returns:
            BaseModel: The execution result from the underlying runnable,
                      typically a Pydantic model instance (e.g., TaskAssessment,
                      TaskRequirement, TaskTeam).

        Raises:
            Exception: Any exception raised by the underlying runnable.

        Example:
            >>> task = create_planning_task("Plan the workflow")
            >>> result = await task.run_async()  # Returns TaskTeam
            >>> print(len(result.specialists))
        """
        result = await self._runnable.run_async(self._query, **kwargs)
        return self._parse_response(result)

    def _parse_response(self, response: Any) -> BaseModel:
        """
        Parse the response using the response_format if provided.

        If response_format is set, attempts to parse the response as JSON
        and convert it to the specified Pydantic model. If response is already
        a BaseModel instance, returns it as-is.

        Args:
            response: The response from the underlying runnable (typically a string)

        Returns:
            BaseModel: The parsed response or the original response if no
                      response_format is set

        Raises:
            json.JSONDecodeError: If response is a string but not valid JSON
            ValueError: If the parsed JSON doesn't match the response_format schema
        """
        # If no response format specified, return as-is
        if self._response_format is None:
            return response

        # If already a BaseModel instance, return as-is
        if isinstance(response, BaseModel):
            return response

        # If response is a string, try to parse as JSON
        if isinstance(response, str):
            try:
                # Try to parse as JSON
                data = json.loads(response)
                # Convert to the response format model
                return self._response_format(**data)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON from the string
                # Look for JSON object or array in the string
                import re

                json_match = re.search(r"\{.*\}|\[.*\]", response, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                        return self._response_format(**data)
                    except (json.JSONDecodeError, ValueError):
                        pass
                # If all parsing fails, raise error
                raise ValueError(
                    f"Could not parse response as JSON for {self._response_format.__name__}: {response}"
                )

        # For other types, try to convert directly
        return self._response_format(**response)

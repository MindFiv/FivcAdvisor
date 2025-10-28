"""
Task Runnable wrapper for agent execution.

This module provides TaskRunnable, a wrapper around agent runnables that
prepends a task-specific query to the execution context.

Key Components:
    - TaskRunnable: Wraps an agent runnable with a task query
"""

from typing import Any, Union

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
                     run_async() methods. If the runnable is an AgentsRunnable
                     with a response_model, the result will be a Pydantic model
                     instance instead of a string.
            **kwargs: Additional keyword arguments (reserved for future use).

        Raises:
            TypeError: If runnable does not implement the Runnable interface.
        """
        self._query = query
        self._runnable = runnable

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

    @property
    def name(self) -> str:
        """
        Get the name of this runnable.

        Returns the name of the underlying runnable, ensuring consistent
        naming across the task execution pipeline.

        Returns:
            str: The name of the underlying runnable.
        """
        return self._runnable.name

    def run(self, **kwargs: Any) -> Union[BaseModel, str]:
        """
        Execute the task synchronously.

        Prepends the task query to the execution and delegates to the
        underlying runnable's run method. The query is passed as a keyword
        argument to the underlying runnable.

        The return type depends on the underlying runnable's response_model:
        - If the runnable has a response_model: Returns a Pydantic model instance
        - If the runnable has no response_model: Returns a string

        Args:
            **kwargs: Additional keyword arguments to pass to the underlying
                     runnable's run method. The task query is automatically
                     prepended as the 'query' parameter.

        Returns:
            Union[BaseModel, str]: The execution result from the underlying runnable.
                                   Typically a Pydantic model instance (e.g., TaskAssessment,
                                   TaskRequirement, TaskTeam) when response_model is set,
                                   or a string otherwise.

        Raises:
            Exception: Any exception raised by the underlying runnable.

        Example:
            >>> task = create_assessing_task("Is this complex?")
            >>> result = task.run()  # Returns TaskAssessment
            >>> print(result.require_planning)
        """
        return self._runnable.run(query=self._query, **kwargs)

    async def run_async(self, **kwargs: Any) -> Union[BaseModel, str]:
        """
        Execute the task asynchronously.

        Prepends the task query to the execution and delegates to the
        underlying runnable's run_async method. The query is passed as a
        keyword argument to the underlying runnable.

        This method is useful for non-blocking execution in async contexts,
        such as web servers or concurrent task processing.

        The return type depends on the underlying runnable's response_model:
        - If the runnable has a response_model: Returns a Pydantic model instance
        - If the runnable has no response_model: Returns a string

        Args:
            **kwargs: Additional keyword arguments to pass to the underlying
                     runnable's run_async method. The task query is automatically
                     prepended as the 'query' parameter.

        Returns:
            Union[BaseModel, str]: The execution result from the underlying runnable.
                                   Typically a Pydantic model instance (e.g., TaskAssessment,
                                   TaskRequirement, TaskTeam) when response_model is set,
                                   or a string otherwise.

        Raises:
            Exception: Any exception raised by the underlying runnable.

        Example:
            >>> task = create_planning_task("Plan the workflow")
            >>> result = await task.run_async()  # Returns TaskTeam
            >>> print(len(result.specialists))
        """
        return await self._runnable.run_async(query=self._query, **kwargs)

"""
Runnable abstract base class for FivcAdvisor utilities.

This module defines the Runnable abstract base class, which specifies the interface
for objects that support both synchronous and asynchronous execution.
"""

from abc import ABC, abstractmethod
from typing import Any


class Runnable(ABC):
    """
    Abstract base class for runnable objects that support sync and async execution.

    This abstract base class defines the interface for objects that can be executed
    in both synchronous and asynchronous contexts. Subclasses must implement both
    `run()` and `run_async()` methods to support different execution patterns.

    Abstract Methods:
        run: Execute the runnable synchronously
        run_async: Execute the runnable asynchronously

    Example:
        >>> class MyRunnable(Runnable):
        ...     def run(self, *args, **kwargs):
        ...         return "sync result"
        ...
        ...     async def run_async(self, *args, **kwargs):
        ...         return "async result"
        ...
        >>> runnable = MyRunnable()
        >>> result = runnable.run()
        >>> async_result = await runnable.run_async()
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Unique identifier for the runnable.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the runnable.
        """

    @abstractmethod
    async def run_async(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the runnable asynchronously (abstract method).

        Subclasses must implement this method to perform the runnable's
        operation in an async context, allowing for non-blocking I/O
        and concurrent execution.

        Args:
            *args: Positional arguments to pass to the runnable
            **kwargs: Keyword arguments to pass to the runnable

        Returns:
            The result of the async execution
        """

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the runnable synchronously (abstract method).

        Subclasses must implement this method to perform the runnable's
        operation in a synchronous context, blocking until completion.

        Args:
            *args: Positional arguments to pass to the runnable
            **kwargs: Keyword arguments to pass to the runnable

        Returns:
            The result of the synchronous execution
        """

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the runnable synchronously.

        This method provides a convenient interface for invoking the runnable
        using the function call syntax. It simply delegates to the `run()` method.

        Args:
            *args: Positional arguments to pass to the runnable
            **kwargs: Keyword arguments to pass to the runnable

        Returns:
            The result of the synchronous execution
        """
        return self.run(*args, **kwargs)

"""
Types module for FivcAdvisor utils.

This module provides core utility types and abstract base classes:
- OutputDir: Context manager for managing output directories
- LazyValue: Lazy-evaluated transparent proxy for deferred computation
- Runnable: Abstract base class for objects supporting sync and async execution
"""

__all__ = [
    "OutputDir",
    "Runnable",
    "LazyValue",
]

from .directories import OutputDir
from .runables import Runnable
from .variables import LazyValue

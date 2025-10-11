"""
Task types module.

Provides types and utilities for task execution tracking and persistence.

Key Components:
    - TaskMonitor: Tracks agent execution through Strands hooks
    - TaskMonitorManager: Manages multiple tasks with centralized monitoring
    - TaskRuntime: Task metadata and execution state
    - TaskRuntimeStep: Individual agent execution step
    - TaskRuntimeRepository: Abstract interface for task persistence
    - TaskStatus: Execution status enumeration (from Strands)
"""

__all__ = [
    "TaskMonitor",
    "TaskRuntimeStep",
    "TaskRuntime",
    "TaskRuntimeRepository",
    "TaskStatus",
    "TaskMonitorManager",
]

from .base import (
    TaskStatus,
    TaskRuntimeStep,
    TaskRuntime,
)
from .monitors import TaskMonitor, TaskMonitorManager
from .repositories import TaskRuntimeRepository

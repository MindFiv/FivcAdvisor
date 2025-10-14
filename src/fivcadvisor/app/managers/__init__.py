"""
Managers module for FivcAdvisor app.

This module provides manager classes for handling application state:
- ChatManager: Manages chat conversation and agent execution
- TaskManager: Manages task execution with UI notifications
"""

__all__ = [
    "ChatManager",
    "TaskManager",
]

from .chat import ChatManager
from .tasks import TaskManager

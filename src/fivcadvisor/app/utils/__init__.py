"""
Utils module for FivcAdvisor app.

This module provides utility classes for handling application state:
- Chat: Manages chat conversation and agent execution
- ChatManager: Manages multiple chat instances
- TaskManager: Manages task execution with UI notifications
"""

__all__ = [
    "Chat",
    "ChatManager",
    "TaskManager",
    "get_current_page_id",
    "set_current_page_id",
]

from fivcadvisor.settings import SettingsConfig
from fivcadvisor.utils import OutputDir

from .chats import Chat, ChatManager
from .tasks import TaskManager


def get_current_page_id():
    """
    Get the current page ID from the URL.

    Returns:
        str: The current page ID
    """
    with OutputDir():
        config = SettingsConfig("run.yml")
        return config.get("page_id")


def set_current_page_id(page_id: str):
    """
    Set the current page ID in the URL.

    Args:
        page_id: The page ID to set
    """
    with OutputDir():
        config = SettingsConfig("run.yml")
        config.set("page_id", page_id)
        config.save()

"""
FivcAdvisor App Views

View implementations for the multi-page application.
Each view inherits from ViewBase and implements the render() method.
"""

__all__ = [
    "ViewBase",
    "ViewNavigation",
    "ChatView",
    "SettingsView",
]

from .base import ViewBase, ViewNavigation
from .chats import ChatView
from .settings import SettingsView

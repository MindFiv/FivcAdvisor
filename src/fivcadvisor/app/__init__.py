"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
Multi-page application with dynamic navigation.
"""

__all__ = [
    "main",
]

import streamlit as st

from fivcadvisor.tools import default_retriever
from fivcadvisor.agents.types.repositories import FileAgentsRuntimeRepository
from fivcadvisor.app.utils import ChatManager
from fivcadvisor.app.views import ViewNavigation, ChatView, SettingsView


def main():
    """Main Streamlit application entry point with custom ViewNavigation"""

    # Page configuration (must be called first)
    st.set_page_config(
        page_title="FivcAdvisor - Intelligent Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    agent_runtime_repo = FileAgentsRuntimeRepository()
    chat_manager = ChatManager(
        agent_runtime_repo=agent_runtime_repo,
        tools_retriever=default_retriever,
    )

    # Create navigation instance
    nav = ViewNavigation()

    # Build chat views
    chat_pages = [ChatView(chat_manager.add_chat())]
    chat_pages.extend([ChatView(chat) for chat in chat_manager.list_chats()])

    # Add sections to navigation
    nav.add_section("Chats", chat_pages)
    nav.add_section(
        "Settings",
        [SettingsView()],
    )

    # Run navigation
    nav.run()


if __name__ == "__main__":
    main()

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
from fivcadvisor.app.managers import ChatManager
from fivcadvisor.app.views import chats, settings


def main():
    """Main Streamlit application entry point with st.navigation"""

    agent_runtime_repo = FileAgentsRuntimeRepository()
    chat_manager = ChatManager(
        agent_runtime_repo=agent_runtime_repo,
        tools_retriever=default_retriever,
    )

    # Get existing chats
    existing_chats = chat_manager.list_chats()

    agent_id = st.session_state.agent_id if "agent_id" in st.session_state else None

    # Create pages for existing chats
    chat_pages = [
        st.Page(
            lambda c=chat: chats.render(c),
            title=chat.description or f"Chat {chat.id[:8]}",
            icon="💬",
            url_path=f"chat-{chat.id}",
            default=agent_id == chat.id,
        )
        for chat in existing_chats
    ]

    # Add "New Chat" page at the beginning
    chat_pages.insert(
        0,
        st.Page(
            lambda: chats.render(chat_manager.add_chat()),
            title="New Chat",
            icon="➕",
            url_path="chat-new",
        ),
    )

    # Page configuration
    st.set_page_config(
        page_title="FivcAdvisor - Intelligent Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Define views with unique url_path
    pages = {
        "Chats": chat_pages,
        "Settings": [
            st.Page(settings.render, title="Settings", icon="⚙️", url_path="settings"),
        ],
    }

    # Create navigation
    pg = st.navigation(pages)

    # Run selected page
    pg.run()


if __name__ == "__main__":
    main()

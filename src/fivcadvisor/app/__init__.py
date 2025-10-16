"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
Multi-page application with dynamic navigation.
"""

__all__ = [
    "main",
]

import functools
import streamlit as st

from fivcadvisor.tools import default_retriever
from fivcadvisor.agents.types.repositories import FileAgentsRuntimeRepository
from fivcadvisor.app.utils import ChatManager, get_current_page_id
from fivcadvisor.app.views import chats, settings


def main():
    """Main Streamlit application entry point with st.navigation"""

    agent_runtime_repo = FileAgentsRuntimeRepository()
    chat_manager = ChatManager(
        agent_runtime_repo=agent_runtime_repo,
        tools_retriever=default_retriever,
    )

    page_id = get_current_page_id()

    # Add "New Chat" page at the beginning
    chat_pages = [
        st.Page(
            lambda: chats.render(chat_manager.add_chat()),
            title="New Chat",
            icon="➕",
            url_path="chat-new",
            default=page_id is None,
        )
    ]
    for chat in chat_manager.list_chats():
        page = st.Page(
            functools.partial(chats.render, chat),
            title=chat.description or f"Chat {chat.id[:8]}",
            icon="💬",
            url_path=f"{chat.id}",
            default=page_id == chat.id,
        )
        chat_pages.append(page)

    # Page configuration
    st.set_page_config(
        page_title="FivcAdvisor - Intelligent Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Create navigation
    pg = st.navigation(
        {
            "Chats": chat_pages,
            "Settings": [
                st.Page(
                    settings.render, title="Settings", icon="⚙️", url_path="settings"
                ),
            ],
        }
    )

    # Run selected page
    pg.run()


if __name__ == "__main__":
    main()

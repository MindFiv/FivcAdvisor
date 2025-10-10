"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
Multi-page application with dynamic navigation.
"""

__all__ = [
    "main",
]

import streamlit as st

from fivcadvisor import agents, tools
from fivcadvisor.app.sessions import ChatSession
from fivcadvisor.app.views import chat, settings


def main():
    """Main Streamlit application entry point with st.navigation"""

    # Page configuration
    st.set_page_config(
        page_title="FivcAdvisor - Intelligent Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize global session (shared across all views)
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = ChatSession(
            agents_retriever=agents.default_retriever,
            tools_retriever=tools.default_retriever,
        )

    # Define views with unique url_path
    pages = {
        "主要功能": [
            st.Page(
                chat.render,
                title="对话",
                icon="💬",
                url_path="chat",
                default=True,
            ),
        ],
        "其他": [
            st.Page(settings.render, title="设置", icon="⚙️", url_path="settings"),
        ],
    }

    # Create navigation
    pg = st.navigation(pages)

    # Run selected page
    pg.run()


if __name__ == "__main__":
    main()

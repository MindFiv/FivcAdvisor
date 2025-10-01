"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
"""

__all__ = [
    "create_default_ui",
    "main",
]

import asyncio

import streamlit as st

from fivcadvisor import agents, tools
from fivcadvisor.app.sessions import ChatSession
from fivcadvisor.app.tools import (
    ToolCallback,
    # ToolsRenderer,
)
from fivcadvisor.app.messages import (
    MessageCallback,
    MessagesRenderer,
)


def create_default_ui():
    """Create the Streamlit interface."""

    # Initialize session state
    chat_session = ChatSession(
        agents_retriever=agents.default_retriever,
        tools_retriever=tools.default_retriever,
    )
    # Page configuration
    st.set_page_config(
        page_title="FivcAdvisor - Intelligent Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.header(":sunglasses: :blue[FivcAdvisor] chills", divider="blue")

    # Sidebar
    with st.sidebar:
        st.header("FivcAdvisor")

    messages_renderer = MessagesRenderer(chat_session.get_history())
    messages_renderer.render()

    if user_query := st.chat_input("Ask me anything..."):
        with st.chat_message("user"):
            st.write(user_query)

        tool_placeholder = st.empty()
        tool_callback = ToolCallback(tool_placeholder)

        with st.chat_message("assistant"):
            stream_placeholder = st.empty()
            stream_callback = MessageCallback(stream_placeholder)

        asyncio.run(
            chat_session.run(
                user_query,
                on_stream=stream_callback,
                on_tool=tool_callback,
            )
        )
        st.rerun()


def main():
    """Main Streamlit application entry point."""
    create_default_ui()


if __name__ == "__main__":
    main()

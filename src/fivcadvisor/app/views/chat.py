"""
Chat Page

Simple conversation mode with streaming responses.
"""

import streamlit as st
import asyncio

from fivcadvisor.app.messages import MessageCallback, MessagesRenderer
from fivcadvisor.app.tools import MessageToolCallback


def render():
    """Render chat page"""

    st.title("💬 对话")

    # Get shared session
    chat_session = st.session_state.chat_session

    # Display history messages
    messages_renderer = MessagesRenderer(chat_session.list_messages())
    messages_renderer.render()

    # User input
    if user_query := st.chat_input("Ask me anything..."):
        with st.chat_message("user"):
            st.write(user_query)

        # Streaming response
        render_simple_response(user_query, chat_session)

        st.rerun()


def render_simple_response(query: str, chat_session):
    """Render simple streaming response"""

    tool_placeholder = st.empty()
    tool_callback = MessageToolCallback(tool_placeholder)

    with st.chat_message("assistant"):
        stream_placeholder = st.empty()
        stream_callback = MessageCallback(stream_placeholder)

    asyncio.run(
        chat_session.run(
            query,
            on_stream=stream_callback,
            on_tool=tool_callback,
        )
    )

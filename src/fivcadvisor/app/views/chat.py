"""
Chat Page

Simple conversation mode with streaming responses.
"""

import streamlit as st
import asyncio

from fivcadvisor import tools
from fivcadvisor.agents.types import AgentsRuntime
from fivcadvisor.app.managers import ChatManager
from fivcadvisor.app.components import chat_message


def render():
    """
    Render the chat page with conversation history and input.

    This function creates a Streamlit chat interface that:
    1. Initializes a ChatManager with the default tools retriever
    2. Displays the page title
    3. Renders all completed agent runtimes from history
    4. Provides a chat input for new queries
    5. Streams responses in real-time using callbacks

    The chat interface uses AgentsRuntime objects to track both
    completed messages (from history) and streaming responses
    (during active agent execution).
    """
    chat = ChatManager(tools_retriever=tools.default_retriever)

    st.title("💬 Chat with FivcAdvisor")

    # Display history messages
    c = st.container()
    for i in chat.list_history():
        chat_message.render(c, i)

    # User input
    if user_query := st.chat_input("Ask me anything..."):
        chat_placeholder = st.empty()

        def _on_event(rt: AgentsRuntime):
            """
            Callback for streaming agent events.

            Updates the chat placeholder with the current runtime state,
            allowing real-time display of streaming responses.

            Args:
                rt: AgentsRuntime with streaming_text and other state
            """
            container = chat_placeholder.container()
            chat_message.render(container, rt)

        asyncio.run(chat.ask(user_query, on_event=_on_event))
        # st.rerun()

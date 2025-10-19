"""
Chat Page

Provides a simple conversation interface with streaming responses.

This module implements the main chat view for the FivcAdvisor web interface,
allowing users to interact with an AI agent through a conversational interface.
The view handles:
- Displaying conversation history
- Accepting user input
- Streaming agent responses in real-time
- Rendering tool calls and thinking processes

The chat uses the Chat utility for state management and the AgentsRuntime
system for tracking execution state and persistence.
"""

import os

import streamlit as st
import asyncio

from fivcadvisor.app.utils import Chat
from fivcadvisor.app.components import chat_message


def render(chat: Chat):
    """
    Render the chat page with conversation history and input.

    Creates a Streamlit chat interface that provides a conversational
    experience with the FivcAdvisor agent. The interface includes:

    1. **Chat Utility Initialization**: Creates a Chat instance with the
       default tools retriever. The Chat utility handles agent execution,
       state persistence, and conversation history.

    2. **Page Title**: Displays the chat page title with an emoji icon.

    3. **Conversation History**: Renders all completed agent runtimes from
       previous queries in chronological order. Each runtime includes the
       user query and agent response.

    4. **User Input**: Provides a chat input field for new queries. When
       the user submits a query, it's sent to the agent asynchronously.

    5. **Streaming Responses**: Uses a callback to render streaming text
       and tool calls in real-time as the agent processes the query.

    The chat interface uses AgentsRuntime objects to track both completed
    messages (from history) and streaming responses (during active agent
    execution). All conversation state is automatically persisted to the
    repository.

    Example Flow:
        1. User opens chat page
        2. Previous conversation history is loaded and displayed
        3. User types a query and presses Enter
        4. Query is sent to agent with streaming callback
        5. Agent response streams in real-time
        6. Completed response is added to history
        7. Page is ready for next query

    Note:
        - The Chat instance is created fresh on each page render
        - Conversation history is loaded from the repository
        - The agent_id is auto-generated and persists across renders
        - Streaming updates are rendered via the on_event callback
        - The default tools retriever provides tools based on the query
    """

    # title_placeholder = st.empty()
    # Display conversation history
    msg_placeholder = st.container()

    runtimes = chat.list_history()
    for runtime in runtimes:
        chat_message.render(runtime, msg_placeholder)

    logo_placeholder = st.empty()
    if not runtimes:
        # Page title
        # title_placeholder.title("💬 FivcAdvisor At Your Service!")
        logo_path = os.path.dirname(os.path.dirname(__file__))
        logo_path = os.path.join(logo_path, "assets", "FivcAdvisor.png")
        _, logo_col, _ = logo_placeholder.columns(3)
        logo_col.image(logo_path, caption="💬 FivcAdvisor At Your Service!")

    # User input field
    if user_query := st.chat_input("Ask me anything..."):
        # Clear logo
        logo_placeholder.empty()

        # Create placeholder for streaming response
        msg_new_placeholder = st.empty()

        # Render user query
        with msg_new_placeholder.chat_message("user"):
            st.text(user_query)

        # Execute query with streaming callback
        # is_new_chat = chat.id is None

        asyncio.run(
            chat.ask(
                user_query,
                on_event=lambda rt: chat_message.render(rt, msg_new_placeholder),
            )
        )

        # if is_new_chat:
        #     # Set the agent_id and rerun to navigate to the new chat
        #     st.session_state.page_id = chat.id
        #     st.rerun()
        # else:
        #     # For existing chats, just update the agent_id
        #     st.session_state.page_id = chat.id

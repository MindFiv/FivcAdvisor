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

The chat uses the Chat manager for state management and the AgentsRuntime
system for tracking execution state and persistence.
"""

import streamlit as st
import asyncio

from fivcadvisor.app.managers import Chat
from fivcadvisor.app.components import chat_message


def render(chat: Chat):
    """
    Render the chat page with conversation history and input.

    Creates a Streamlit chat interface that provides a conversational
    experience with the FivcAdvisor agent. The interface includes:

    1. **Chat Manager Initialization**: Creates a Chat instance with the
       default tools retriever. The Chat manager handles agent execution,
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

    # Page title
    st.title("💬 Chat with FivcAdvisor")

    # Display conversation history
    chat_placeholder = st.container()
    for runtime in chat.list_history():
        chat_message.render(runtime, chat_placeholder)

    # User input field
    if user_query := st.chat_input("Ask me anything..."):
        # Create placeholder for streaming response
        chat_placeholder = st.empty()

        # Render user query
        with chat_placeholder.chat_message("user"):
            st.text(user_query)

        # Execute query with streaming callback
        asyncio.run(
            chat.ask(
                user_query,
                on_event=lambda rt: chat_message.render(rt, chat_placeholder),
            )
        )

        # Save agent ID in session state for future reference
        st.session_state.agent_id = chat.id
        # Rerun to refresh the navigation sidebar with new chat
        st.rerun()

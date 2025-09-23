"""
FivcAdvisor Chat Box

A reusable chat interface component for FivcAdvisor with Agent functionality.
"""

from typing import Any, Dict, List, Optional, Callable
import streamlit as st
from .chat_message import ChatMessageRenderer


class ChatBox:
    """
    A reusable chat box for FivcAdvisor Agent interactions.

    This component encapsulates all chat-related functionality including:
    - Message display and management
    - User input handling
    - Example queries
    - Session state management
    """

    def __init__(
        self,
        process_message_callback: Callable[[str, str, bool], str | Dict[str, Any]],
        get_example_queries_callback: Optional[Callable[[], List[str]]] = None,
        session_key_prefix: str = "chat",
        placeholder_text: str = "Ask me anything...",
        show_examples: bool = True,
        max_examples: int = 4,
    ):
        """
        Initialize the chat box.

        Args:
            process_message_callback: Function to process user messages
            get_example_queries_callback: Function to get example queries
            session_key_prefix: Prefix for session state keys
            placeholder_text: Placeholder text for chat input
            show_examples: Whether to show example queries
            max_examples: Maximum number of example queries to show
        """
        self.process_message_callback = process_message_callback
        self.get_example_queries_callback = get_example_queries_callback
        self.session_key_prefix = session_key_prefix
        self.placeholder_text = placeholder_text
        self.show_examples = show_examples
        self.max_examples = max_examples

        # Session state keys
        self.messages_key = f"{session_key_prefix}_messages"

        # Initialize message renderer
        self.message_renderer = ChatMessageRenderer(session_key_prefix)

        # Initialize session state
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state for chat messages."""
        if self.messages_key not in st.session_state:
            st.session_state[self.messages_key] = []

    def clear_chat(self):
        """Clear all chat messages."""
        st.session_state[self.messages_key] = []

    def add_message(self, role: str, content, reasoning: str = None):
        """Add a message to the chat history."""
        message_data = {"role": role, "content": content}

        # Handle structured responses for assistant messages
        if role == "assistant" and isinstance(content, dict):
            message_data.update(
                {
                    "type": content.get("type", "simple"),
                    "content": content.get("content", ""),
                    "answer": content.get("answer"),
                    "reasoning": content.get("reasoning"),
                }
            )
        elif reasoning:
            message_data["reasoning"] = reasoning

        st.session_state[self.messages_key].append(message_data)

    def get_messages(self) -> List[Dict[str, str]]:
        """Get all chat messages."""
        return st.session_state[self.messages_key]

    def render_messages(self):
        """Render all chat messages using the message renderer."""
        messages = self.get_messages()
        self.message_renderer.render_messages(messages)

    def get_example_queries(self) -> List[str]:
        """Get example queries from callback."""
        if self.get_example_queries_callback:
            return self.get_example_queries_callback()
        return []

    def _handle_example_query(self, query: str, graph_type: str, verbose: bool):
        """Handle example query selection."""
        self.add_message("user", query)
        with st.spinner("Processing..."):
            response = self.process_message_callback(query, graph_type, verbose)
        self.add_message("assistant", response)
        st.rerun()

    def render_chat_input(self, graph_type: str, verbose: bool):
        """Render the chat input and handle user messages."""
        if prompt := st.chat_input(self.placeholder_text):
            # Add user message to chat history
            self.add_message("user", prompt)

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.spinner("Processing your request..."):
                response = self.process_message_callback(prompt, graph_type, verbose)

            # Format and render the response using message component
            if isinstance(response, dict):
                # Already structured response
                formatted_response = {"role": "assistant", **response}
            else:
                # Simple string response
                formatted_response = {
                    "role": "assistant",
                    "content": str(response),
                    "type": "simple",
                }

            # Render the response using message component
            self.message_renderer.render_single_message(
                formatted_response, len(self.get_messages())
            )

            # Add assistant response to chat history
            self.add_message("assistant", response)

    def render_full_chat_interface(
        self, graph_type: str, verbose: bool, title: str = "💬 Chat"
    ):
        """
        Render the complete chat interface.

        Args:
            graph_type: The selected graph type
            verbose: Whether verbose mode is enabled
            title: Title for the chat section
        """
        st.subheader(title)

        # Display chat messages
        self.render_messages()

        # Chat input
        self.render_chat_input(graph_type, verbose)


def create_default_chat_box(
    process_message_callback: Callable[[str, str, bool], str | Dict[str, Any]],
    get_example_queries_callback: Optional[Callable[[], List[str]]] = None,
) -> ChatBox:
    """
    Create a default chat box with standard settings.

    Args:
        process_message_callback: Function to process user messages
        get_example_queries_callback: Function to get example queries

    Returns:
        Configured ChatBox instance
    """
    return ChatBox(
        process_message_callback=process_message_callback,
        get_example_queries_callback=get_example_queries_callback,
        session_key_prefix="fivcadvisor_chat",
        placeholder_text="Ask me anything...",
        show_examples=True,
        max_examples=4,
    )

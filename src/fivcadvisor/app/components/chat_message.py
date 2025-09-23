"""
FivcAdvisor Chat Message Component

A specialized component for rendering different types of chat messages,
particularly Agent responses with expandable reasoning sections.
"""

from typing import Dict, Any, Optional
import streamlit as st


class ChatMessage:
    """
    A component for rendering chat messages with support for different message types.

    Supports:
    - Simple text messages
    - Structured responses with expandable reasoning
    - Error messages with special formatting
    - User messages
    """

    def __init__(self, session_key_prefix: str = "chat_message"):
        """
        Initialize the chat message component.

        Args:
            session_key_prefix: Prefix for session state keys to avoid conflicts
        """
        self.session_key_prefix = session_key_prefix

    def render(self, message: Dict[str, Any], message_index: int = 0):
        """
        Render a chat message based on its type and content.

        Args:
            message: Message data dictionary
            message_index: Index of the message for unique keys
        """
        role = message.get("role", "user")

        with st.chat_message(role):
            if role == "assistant":
                self._render_assistant_message(message, message_index)
            else:
                self._render_user_message(message)

    def _render_assistant_message(self, message: Dict[str, Any], message_index: int):
        """Render assistant message with appropriate formatting."""
        message_type = message.get("type", "simple")

        if message_type == "error":
            self._render_error_message(message)
        elif message_type == "structured" and message.get("reasoning"):
            self._render_structured_message(message, message_index)
        else:
            self._render_simple_message(message)

    def _render_user_message(self, message: Dict[str, Any]):
        """Render user message."""
        content = self._extract_content(message)
        st.markdown(content)

    def _render_simple_message(self, message: Dict[str, Any]):
        """Render simple assistant message without reasoning."""
        content = self._extract_content(message)
        st.markdown(content)

    def _render_error_message(self, message: Dict[str, Any]):
        """Render error message with special styling."""
        content = self._extract_content(message)
        st.error(content)

    def _render_structured_message(self, message: Dict[str, Any], message_index: int):
        """Render structured message with expandable reasoning."""
        # Display the main answer
        content = self._extract_content(message)
        st.markdown(content)

        # Display expandable reasoning section
        reasoning = message.get("reasoning", "")
        if reasoning:
            self._render_reasoning_section(reasoning, message_index)

    def _render_reasoning_section(self, reasoning: str, message_index: int):
        """Render expandable reasoning section."""
        reasoning_key = f"{self.session_key_prefix}_reasoning_{message_index}"

        with st.expander("🤔 View Reasoning", expanded=False):
            st.markdown("**Agent's Thought Process:**")
            st.text_area(
                "Reasoning",
                value=reasoning,
                height=150,
                disabled=True,
                key=f"{reasoning_key}_textarea",
                label_visibility="collapsed",
            )

    def _extract_content(self, message: Dict[str, Any]) -> str:
        """Extract content from message, handling different formats."""
        content = message.get("content", "")

        # Handle structured content
        if isinstance(content, dict):
            return content.get("content", str(content))

        # Handle string content
        return str(content) if content else ""


class ChatMessageRenderer:
    """
    A higher-level renderer for managing multiple chat messages.

    This class provides batch rendering capabilities and manages
    message state across multiple renders.
    """

    def __init__(self, session_key_prefix: str = "chat_renderer"):
        """
        Initialize the chat message renderer.

        Args:
            session_key_prefix: Prefix for session state keys
        """
        self.session_key_prefix = session_key_prefix
        self.message_component = ChatMessage(session_key_prefix)

    def render_messages(self, messages: list):
        """
        Render a list of chat messages.

        Args:
            messages: List of message dictionaries
        """
        for i, message in enumerate(messages):
            self.message_component.render(message, i)

    def render_single_message(self, message: Dict[str, Any], message_index: int = 0):
        """
        Render a single chat message.

        Args:
            message: Message data dictionary
            message_index: Index of the message for unique keys
        """
        self.message_component.render(message, message_index)


def create_chat_message_renderer(
    session_key_prefix: str = "default_chat",
) -> ChatMessageRenderer:
    """
    Create a default chat message renderer with standard settings.

    Args:
        session_key_prefix: Prefix for session state keys

    Returns:
        Configured ChatMessageRenderer instance
    """
    return ChatMessageRenderer(session_key_prefix)


# Utility functions for message formatting
def format_user_message(content: str) -> Dict[str, Any]:
    """Format a user message."""
    return {"role": "user", "content": content, "type": "simple"}


def format_assistant_message(
    content: str, reasoning: Optional[str] = None, message_type: str = "simple"
) -> Dict[str, Any]:
    """
    Format an assistant message.

    Args:
        content: Main message content
        reasoning: Optional reasoning/thought process
        message_type: Type of message ("simple", "structured", "error")

    Returns:
        Formatted message dictionary
    """
    message = {"role": "assistant", "content": content, "type": message_type}

    if reasoning:
        message["reasoning"] = reasoning
        message["type"] = "structured"

    return message


def format_error_message(error_text: str) -> Dict[str, Any]:
    """Format an error message."""
    return {
        "role": "assistant",
        "content": f"❌ **Error:** {error_text}",
        "type": "error",
    }


def format_structured_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a structured response from agent data.

    Args:
        response_data: Response data with potential answer/reasoning fields

    Returns:
        Formatted message dictionary
    """
    if isinstance(response_data, dict):
        content = response_data.get("content", response_data.get("answer", ""))
        reasoning = response_data.get("reasoning")
        message_type = response_data.get(
            "type", "structured" if reasoning else "simple"
        )

        return format_assistant_message(content, reasoning, message_type)
    else:
        return format_assistant_message(str(response_data))

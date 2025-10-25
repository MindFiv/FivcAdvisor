"""
Event and message types for FivcAdvisor.

This module provides custom types and adapters for handling messages and events
in the FivcAdvisor system, using LangChain types as the foundation.
"""

from typing import Any, Dict, Union, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage


class StreamEvent:
    """
    Represents a streaming event.

    This class wraps streaming events to provide a consistent interface
    for handling different types of streaming data (text, tool calls, etc.).

    Attributes:
        event_type: Type of the event (e.g., 'text', 'tool_call', 'tool_result')
        data: The event data payload

    Example:
        >>> event = StreamEvent("text", "Hello, world!")
        >>> print(event.event_type)
        'text'
        >>> print(event.data)
        'Hello, world!'
    """

    def __init__(self, event_type: str, data: Any):
        """
        Initialize a StreamEvent.

        Args:
            event_type: Type of the event
            data: The event data payload
        """
        self.event_type = event_type
        self.data = data

    def __repr__(self) -> str:
        return f"StreamEvent(event_type={self.event_type!r}, data={self.data!r})"

    def __str__(self) -> str:
        return f"StreamEvent({self.event_type})"


class MessageDictAdapter:
    """
    Adapter to make LangChain BaseMessage objects behave like dicts.

    This adapter wraps a BaseMessage and provides dict-like access to its
    properties, allowing existing code that expects dict-like message access
    to work with LangChain messages.

    Example:
        >>> from langchain_core.messages import AIMessage
        >>> msg = AIMessage(content="Hello")
        >>> adapted = MessageDictAdapter(msg)
        >>> adapted["content"]  # Returns [{"type": "text", "text": "Hello"}]
        >>> adapted["role"]     # Returns "assistant"
    """

    def __init__(self, message: Union[BaseMessage, Dict[str, Any]]):
        """Initialize adapter with either a BaseMessage or dict."""
        self._message = message
        self._is_dict = isinstance(message, dict)

    def __getitem__(self, key: str) -> Any:
        """Get message property using dict-like syntax."""
        # If already a dict, just return the value
        if self._is_dict:
            return self._message.get(key)

        # Handle BaseMessage objects
        if key == "role":
            # Map LangChain message types to role names
            if isinstance(self._message, AIMessage):
                return "assistant"
            elif isinstance(self._message, HumanMessage):
                return "user"
            elif isinstance(self._message, ToolMessage):
                return "tool"
            else:
                return "assistant"
        elif key == "content":
            # Return content as a list of content blocks for compatibility
            content = self._message.content
            if isinstance(content, str):
                return [{"type": "text", "text": content}]
            elif isinstance(content, list):
                return content
            else:
                return [{"type": "text", "text": str(content)}]
        else:
            # Try to get attribute from message
            return getattr(self._message, key, None)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set message property using dict-like syntax."""
        if self._is_dict:
            self._message[key] = value
        else:
            setattr(self._message, key, value)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in message."""
        if self._is_dict:
            return key in self._message
        return hasattr(self._message, key) or key in ["role", "content"]

    def get(self, key: str, default: Any = None) -> Any:
        """Get message property with default value."""
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    def __repr__(self) -> str:
        return f"MessageDictAdapter({self._message!r})"


class AgentResult(BaseModel):
    """
    Agent execution result.

    Represents the result of an agent execution, including the final message
    and any output text.

    Attributes:
        message: The final message from the agent
        output: The output text from the agent
    """

    message: Optional[BaseMessage] = Field(
        default=None, description="Final message from agent"
    )
    output: str = Field(default="", description="Output text from agent")


class SlidingWindowConversationManager:
    """
    Manages conversation history with a sliding window.

    Keeps only the most recent N messages to manage context window size.

    Attributes:
        window_size: Maximum number of messages to keep in history
    """

    def __init__(self, window_size: int = 30):
        """
        Initialize the conversation manager.

        Args:
            window_size: Maximum number of messages to keep
        """
        self.window_size = window_size
        self.messages: List[BaseMessage] = []

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the conversation history."""
        self.messages.append(message)
        # Keep only the most recent window_size messages
        if len(self.messages) > self.window_size:
            self.messages = self.messages[-self.window_size :]

    def get_messages(self) -> List[BaseMessage]:
        """Get all messages in the current window."""
        return self.messages.copy()

    def clear(self) -> None:
        """Clear all messages."""
        self.messages = []


__all__ = [
    "StreamEvent",
    "MessageDictAdapter",
    "AgentResult",
    "SlidingWindowConversationManager",
]

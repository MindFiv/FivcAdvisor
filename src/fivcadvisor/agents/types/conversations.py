"""Custom conversation manager"""

from typing import TYPE_CHECKING, Any, Optional
from strands.agent.conversation_manager import ConversationManager

if TYPE_CHECKING:
    from strands.agent import Agent


class ToolFilteringConversationManager(ConversationManager):
    """
    Conversation manager that filters tool calls (using composition pattern)

    Uses composition pattern to wrap other ConversationManager, focusing on filtering toolUse and toolResult content blocks.
    Executes tool filtering logic first, then delegates to the internal ConversationManager to execute its management strategy.
    This can significantly reduce the number of tokens sent to the LLM and speed up response time.

    Design advantages:
    - Single responsibility: only responsible for tool message filtering
    - Flexible composition: can wrap any ConversationManager
    - Follows "composition over inheritance" principle

    Example:
        >>> from strands.agent import SlidingWindowConversationManager
        >>> from fivcadvisor.agents.types.conversations import ToolFilteringConversationManager
        >>>
        >>> # Compose with sliding window manager
        >>> conversation_manager = SlidingWindowConversationManager(window_size=40)
        >>> conversation_manager = ToolFilteringConversationManager(
        ...     conversation_manager=conversation_manager
        ... )
        >>> agent = Agent(conversation_manager=conversation_manager)
    """

    def __init__(
        self,
        conversation_manager: ConversationManager,
    ):
        self.conversation_manager = conversation_manager
        super().__init__()

    def apply_management(self, agent: "Agent", **kwargs: Any) -> None:
        messages = agent.messages
        message_count_before = len(messages)

        filtered_messages = []
        for m in messages:
            # Filter out toolUse and toolResult, only keep text content
            filtered_content = [
                block
                for block in m.get("content", [])
                if "toolUse" not in block and "toolResult" not in block
            ]

            # If there's still content after filtering, update the message
            # If there's no content after filtering, keep the original message (avoid completely empty messages)
            if filtered_content:
                m["content"] = filtered_content
                filtered_messages.append(m)

        messages[:] = filtered_messages[:]

        self.conversation_manager.apply_management(agent, **kwargs)

        message_count_after = len(agent.messages)
        self.removed_message_count += message_count_after - message_count_before

    def reduce_context(
        self, agent: "Agent", e: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        message_count_before = len(agent.messages)
        self.conversation_manager.reduce_context(agent, e, **kwargs)
        message_count_after = len(agent.messages)
        self.removed_message_count += message_count_after - message_count_before

    def get_state(self) -> dict[str, Any]:
        """Get the current state of the ToolFilteringConversationManager.

        Returns a JSON-serializable dictionary containing:
        - The wrapper's own state (class name and removed_message_count)
        - The wrapped conversation_manager's state
        - The wrapped manager's class information for reconstruction

        Returns:
            dict: A dictionary with the following structure:
                {
                    "__name__": "ToolFilteringConversationManager",
                    "removed_message_count": int,
                    "wrapped_manager_state": dict,  # State from the wrapped manager
                    "wrapped_manager_class": str,   # Class name of wrapped manager
                    "wrapped_manager_init_params": dict  # Init params if available
                }
        """
        # Get the wrapped manager's state
        wrapped_state = self.conversation_manager.get_state()

        # Extract initialization parameters from the wrapped manager if possible
        wrapped_init_params = {}
        if hasattr(self.conversation_manager, "window_size"):
            wrapped_init_params["window_size"] = self.conversation_manager.window_size
        if hasattr(self.conversation_manager, "should_truncate_results"):
            wrapped_init_params["should_truncate_results"] = (
                self.conversation_manager.should_truncate_results
            )

        return {
            "__name__": self.__class__.__name__,
            "removed_message_count": self.removed_message_count,
            "wrapped_manager_state": wrapped_state,
            "wrapped_manager_class": wrapped_state.get(
                "__name__", self.conversation_manager.__class__.__name__
            ),
            "wrapped_manager_init_params": wrapped_init_params,
        }

    def restore_from_session(self, state: dict[str, Any]) -> Optional[Any]:
        """Restore the ToolFilteringConversationManager's state from a session.

        This method restores both the wrapper's state and the wrapped conversation_manager's state.
        It validates that the state matches this class and then delegates to the wrapped manager.

        Args:
            state: Previous state dictionary from get_state(), containing:
                - __name__: Must match "ToolFilteringConversationManager"
                - removed_message_count: The count to restore
                - wrapped_manager_state: State to pass to the wrapped manager

        Returns:
            Optional list of messages to prepend to the agent's messages (from wrapped manager)

        Raises:
            ValueError: If the state's __name__ doesn't match this class
        """
        # Validate that this state is for ToolFilteringConversationManager
        if state.get("__name__") != self.__class__.__name__:
            raise ValueError(
                f"Invalid conversation manager state. Expected '{self.__class__.__name__}', "
                f"got '{state.get('__name__')}'"
            )

        # Restore this manager's state
        self.removed_message_count = state.get("removed_message_count", 0)

        # Restore the wrapped manager's state
        wrapped_state = state.get("wrapped_manager_state")
        if wrapped_state:
            return self.conversation_manager.restore_from_session(wrapped_state)

        return None

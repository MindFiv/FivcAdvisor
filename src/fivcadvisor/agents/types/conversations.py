"""自定义的对话管理器"""

from typing import TYPE_CHECKING, Any, Optional
from strands.agent.conversation_manager import ConversationManager

if TYPE_CHECKING:
    from strands.agent import Agent


class ToolFilteringConversationManager(ConversationManager):
    """
    过滤工具调用的对话管理器（使用组合模式）

    使用组合模式包装其他 ConversationManager，专注于过滤 toolUse 和 toolResult 内容块。
    先执行工具过滤逻辑，然后委托给内部的 ConversationManager 执行其管理策略。
    这样可以大幅减少发送给 LLM 的 token 数量，加快响应速度。

    设计优势：
    - 单一职责：只负责工具消息过滤
    - 灵活组合：可以包装任何 ConversationManager
    - 符合"组合优于继承"原则

    Example:
        >>> from strands.agent import SlidingWindowConversationManager
        >>> from fivcadvisor.agents.types.conversations import ToolFilteringConversationManager
        >>>
        >>> # 组合滑动窗口管理器
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

    @property
    def removed_message_count(self):
        return self.conversation_manager.removed_message_count

    @removed_message_count.setter
    def removed_message_count(self, value: int):
        self.conversation_manager.removed_message_count = value

    def apply_management(self, agent: "Agent", **kwargs: Any) -> None:
        messages = agent.messages

        filtered_messages = []
        for m in messages:
            # 过滤掉 toolUse 和 toolResult，只保留文本内容
            filtered_content = [
                block
                for block in m.get("content", [])
                if "toolUse" not in block and "toolResult" not in block
            ]

            # 如果过滤后还有内容，则更新消息
            # 如果过滤后没有内容了，保留原消息（避免完全空的消息）
            if filtered_content:
                m["content"] = filtered_content
                filtered_messages.append(m)

        messages[:] = filtered_messages[:]
        return self.conversation_manager.apply_management(agent, **kwargs)

    def reduce_context(
        self, agent: "Agent", e: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        return self.conversation_manager.reduce_context(agent, e, **kwargs)

    def get_state(self) -> dict[str, Any]:
        return self.conversation_manager.get_state()

    def restore_from_session(self, state: dict[str, Any]) -> Optional[Any]:
        return self.conversation_manager.restore_from_session(state)

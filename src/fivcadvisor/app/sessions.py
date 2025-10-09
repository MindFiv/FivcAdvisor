import uuid
from typing import Optional, Callable, List, cast

import streamlit as st
from strands.agent import (
    AgentResult,
    SlidingWindowConversationManager,
    # SummarizingConversationManager,
)
from strands.types.session import Message, SessionMessage
from strands.types.streaming import StreamEvent
from strands.session import FileSessionManager

from fivcadvisor import agents, tools, settings, utils


class ChatSession(object):
    def __init__(
        self,
        agents_retriever: Optional[agents.AgentsRetriever] = None,
        tools_retriever: Optional[tools.ToolsRetriever] = None,
        **kwargs,
    ):
        assert agents_retriever is not None
        self.agents_retriever = agents_retriever
        assert tools_retriever is not None
        self.tools_retriever = tools_retriever

        self.session_manager = FileSessionManager(
            self.session_id,
            str(utils.OutputDir().subdir("sessions")),
        )
        self.on_tool: Optional[Callable] = None
        self.on_stream: Optional[Callable] = None
        self.agent_is_running = False

        # 使用组合模式：工具过滤 + 滑动窗口管理
        self.agent = agents.create_companion_agent(
            conversation_manager=agents.ToolFilteringConversationManager(
                SlidingWindowConversationManager()
            ),
            session_manager=self.session_manager,
            callback_handler=self._on_callback,
        )

    @property
    def session_id(self):
        if "session_id" not in st.session_state:
            with utils.OutputDir():
                config = settings.SettingsConfig("run.yml")
                st.session_state.session_id = config.get(
                    "session_id", str(uuid.uuid4())
                )
        return st.session_state.session_id

    def cleanup(self):
        session_id = str(uuid.uuid4())
        with utils.OutputDir():
            config = settings.SettingsConfig("run.yml")
            config.set("session_id", session_id)
            config.save()

        st.session_state.session_id = session_id

        self.session_manager = FileSessionManager(
            session_id,
            str(utils.OutputDir().subdir("sessions")),
        )
        # 使用组合模式：工具过滤 + 滑动窗口管理
        self.agent = agents.create_companion_agent(
            conversation_manager=agents.ToolFilteringConversationManager(
                SlidingWindowConversationManager()
            ),
            session_manager=self.session_manager,
            callback_handler=self._on_callback,
        )

    @property
    def is_running(self):
        return self.agent_is_running

    def list_messages(self) -> List[SessionMessage]:
        return self.session_manager.list_messages(
            self.session_manager.session_id,
            self.agent.agent_id,
        )

    async def run(
        self,
        query: str,
        on_tool: Optional[Callable] = None,
        on_stream: Optional[Callable] = None,
        **kwargs,
    ) -> AgentResult:
        if self.agent_is_running:
            raise ValueError("Previous query not answered")

        try:
            self.on_tool = on_tool
            self.on_stream = on_stream
            self.agent_is_running = True
            return await self.agent.invoke_async(query)
        finally:
            self.agent_is_running = False

    def _on_callback(self, **kwargs):
        if "event" in kwargs:
            event = cast(StreamEvent, kwargs["event"])
            if "contentBlockDelta" in event:
                chunk = event["contentBlockDelta"].get("delta", {})
                chunk = chunk and chunk.get("text")
                if self.on_stream and isinstance(chunk, str):
                    self.on_stream(chunk)

            # elif "messageStop" in event:
            #     if self.on_stream:
            #         self.on_stream("")

        elif "message" in kwargs:
            message = cast(Message, kwargs["message"])
            for content in message.get("content"):
                if "toolUse" in content or "toolResult" in content:
                    if self.on_tool:
                        self.on_tool(content)

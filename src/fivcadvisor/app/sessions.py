import uuid
from typing import Optional, Callable, List

import streamlit as st
from strands.agent import (
    AgentResult,
    SummarizingConversationManager,
)
from strands.session import (
    FileSessionManager,
)
from strands.types.session import SessionMessage

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
        self.agent = agents.create_companion_agent(
            session_manager=self.session_manager,
            conversation_manager=SummarizingConversationManager(),
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

    @property
    def is_running(self):
        return self.agent_is_running

    def get_history(self) -> List[SessionMessage]:
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
        if "data" in kwargs:
            if self.on_stream:
                self.on_stream(kwargs["data"])

        elif "message" in kwargs:
            message = kwargs["message"]
            for block in message["content"]:
                if "toolUse" in block or "toolResult" in block:
                    if self.on_tool:
                        self.on_tool(block)

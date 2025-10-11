import uuid
from typing import Optional, Callable, List

import streamlit as st
from strands.agent import (
    AgentResult,
    SlidingWindowConversationManager,
    # SummarizingConversationManager,
)
from strands.types.session import SessionMessage
from strands.session import FileSessionManager

from fivcadvisor import agents, tools, settings, utils
from fivcadvisor.agents.types import AgentsMonitor


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
        self.monitor = AgentsMonitor()
        self.agent_is_running = False

        # 使用组合模式：工具过滤 + 滑动窗口管理
        self.agent = agents.create_companion_agent(
            conversation_manager=agents.ToolFilteringConversationManager(
                SlidingWindowConversationManager()
            ),
            session_manager=self.session_manager,
            callback_handler=self.monitor,
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
        # Clean up monitor state for new session
        self.monitor.cleanup()
        # 使用组合模式：工具过滤 + 滑动窗口管理
        self.agent = agents.create_companion_agent(
            conversation_manager=agents.ToolFilteringConversationManager(
                SlidingWindowConversationManager()
            ),
            session_manager=self.session_manager,
            callback_handler=self.monitor,
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
        on_event: Optional[Callable] = None,
        **kwargs,
    ) -> AgentResult:
        """
        Execute agent query with optional event callback.

        Args:
            query: User query to process
            on_event: Optional callback receiving AgentsRuntime after each event.
                      Provides access to streaming_text, tool_calls, and other
                      execution state.
            **kwargs: Additional arguments passed to agent

        Returns:
            AgentResult from the agent execution

        Raises:
            ValueError: If agent is already running
        """
        if self.agent_is_running:
            raise ValueError("Previous query not answered")

        try:
            # Clean up monitor for new execution and set callback
            self.monitor.cleanup(on_event=on_event)

            self.agent_is_running = True
            return await self.agent.invoke_async(query)
        finally:
            self.agent_is_running = False

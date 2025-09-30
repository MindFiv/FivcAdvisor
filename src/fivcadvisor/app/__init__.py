"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
"""

__all__ = [
    "create_default_ui",
    "main",
]

import asyncio

import streamlit as st
from strands.types.session import SessionMessage

from fivcadvisor import agents, tools
from fivcadvisor.app.sessions import ChatSession
from fivcadvisor.app.tools import ToolCallback, ToolTraceList


class StreamCallback(object):
    def __init__(self, placeholder):
        self.text = ""
        self.placeholder = placeholder

    def __call__(self, data: str):
        self.text += data
        self.placeholder.markdown(self.text)


def render_message(message: SessionMessage, tool_traces: ToolTraceList):
    msg = message.to_message()
    msg_role = msg["role"]
    msg_content = msg["content"]

    # First pass: process all tool use and result blocks
    for block in msg_content:
        if "text" in block:
            with st.chat_message(msg_role):
                st.markdown(block["text"])

        if "toolUse" in block:
            tool_traces.begin(block["toolUse"])

        if "toolResult" in block:
            tool_traces.end(block["toolResult"])

    tool_traces.render(force=False)


def create_default_ui():
    """Create the Streamlit interface."""

    # Initialize session state
    chat_session = ChatSession(
        agents_retriever=agents.default_retriever,
        tools_retriever=tools.default_retriever,
    )
    # Page configuration
    st.set_page_config(
        page_title="FivcAdvisor - Intelligent Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.header(":sunglasses: :blue[FivAdvisor] chills", divider="blue")

    # Sidebar
    with st.sidebar:
        st.header("FivcAdvisor")

    tool_traces = ToolTraceList()
    for msg in chat_session.get_history():
        render_message(msg, tool_traces)

    if user_query := st.chat_input("Ask me anything..."):
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            tool_placeholder = st.empty()
            stream_placeholder = st.empty()
            stream_placeholder.write("...")

            on_tool = ToolCallback(tool_placeholder)
            on_stream = StreamCallback(stream_placeholder)
            asyncio.run(
                chat_session.run(
                    user_query,
                    on_stream=on_stream,
                    on_tool=on_tool,
                )
            )


def main():
    """Main Streamlit application entry point."""
    create_default_ui()


if __name__ == "__main__":
    main()

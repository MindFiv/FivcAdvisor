"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
"""

__all__ = [
    "create_default_ui",
    "main",
]

import asyncio
from typing import Optional

import streamlit as st
from strands.types.content import Message

from fivcadvisor import agents, tools
from fivcadvisor.app.sessions import ChatSession
from fivcadvisor.app.tools import ToolCallback, ToolTraceList


class StreamCallback(object):
    loading_indicator = """
    <style>
    @keyframes dots {
        0%, 20% {
            content: '●';
        }
        40% {
            content: '●●';
        }
        60%, 100% {
            content: '●●●';
        }
    }
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.7;
            transform: scale(1.15);
        }
    }
    @keyframes glow {
        0%, 100% {
            text-shadow: 0 0 5px #3498db, 0 0 10px #3498db;
        }
        50% {
            text-shadow: 0 0 10px #3498db, 0 0 20px #3498db, 0 0 30px #5dade2;
        }
    }
    .loading-dots {
        display: inline-block;
        margin-left: 6px;
        font-size: 1.0em;
        font-weight: bold;
        color: #3498db;
        animation: pulse 1.5s ease-in-out infinite, glow 2s ease-in-out infinite;
    }
    .loading-dots::after {
        content: '●●●';
        animation: dots 1.2s infinite;
    }
    </style>
    """

    def __init__(self, placeholder):
        self.text = ""
        self.placeholder = placeholder
        text_with_loading = "<span class='loading-dots'></span>"
        self.placeholder.markdown(
            self.loading_indicator + text_with_loading, unsafe_allow_html=True
        )

    def __call__(self, data: Optional[str]):
        self.text += data
        # Display text with animated loading dots
        text_with_loading = f"{self.text}<span class='loading-dots'></span>"
        self.placeholder.markdown(
            self.loading_indicator + text_with_loading, unsafe_allow_html=True
        )


def render_message(message: Message, tool_traces: Optional[ToolTraceList] = None):
    msg = message
    msg_role = msg["role"]
    msg_content = msg["content"]

    # First pass: process all tool use and result blocks
    for block in msg_content:
        if "text" in block:
            with st.chat_message(msg_role):
                st.markdown(block["text"])

        if "toolUse" in block:
            if tool_traces:
                tool_traces.begin(block["toolUse"])

        if "toolResult" in block:
            if tool_traces:
                tool_traces.end(block["toolResult"])

    if tool_traces:
        tool_traces.render()


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
        render_message(msg.to_message(), tool_traces)

    if user_query := st.chat_input("Ask me anything..."):
        with st.chat_message("user"):
            st.write(user_query)

        tool_placeholder = st.empty()
        tool_callback = ToolCallback(tool_placeholder)

        with st.chat_message("assistant"):
            stream_placeholder = st.empty()
            stream_callback = StreamCallback(stream_placeholder)

        asyncio.run(
            chat_session.run(
                user_query,
                on_stream=stream_callback,
                on_tool=tool_callback,
            )
        )
        st.rerun()


def main():
    """Main Streamlit application entry point."""
    create_default_ui()


if __name__ == "__main__":
    main()

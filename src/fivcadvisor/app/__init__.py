"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
"""

__all__ = [
    "create_default_ui",
    "main",
]

import asyncio
from typing import List

import streamlit as st
from strands.types.session import SessionMessage
from strands.types.tools import ToolResult, ToolUse

from fivcadvisor import agents, tools
from fivcadvisor.app.sessions import ChatSession


class ToolTrace(object):
    def __init__(self):
        self.tool_begin = {}
        self.tool_end = {}

    def begin(self, tool_use: ToolUse):
        self.tool_begin = tool_use

    def end(self, tool_result: ToolResult):
        self.tool_end = tool_result

    @property
    def is_complete(self):
        return bool(self.tool_begin) and bool(self.tool_end)

    def render(self, clear=True):
        """Render a tool use block in a user-friendly way."""
        if not self.is_complete:
            return

        tool_use_block = self.tool_begin
        tool_result_block = self.tool_end

        if clear:
            self.tool_begin = {}
            self.tool_end = {}

        try:
            tool_name = tool_use_block.get("name", "Unknown Tool")
            tool_id = tool_use_block.get("toolUseId", "")
            tool_input = tool_use_block.get("input", {})

            # Extract tool result information
            tool_result_id = tool_result_block.get("toolUseId", "")
            tool_content = tool_result_block.get("content", "")
            is_error = tool_result_block.get("status", "") == "error"

            # Create an expander with the tool name and a tool icon
            with st.expander(f"🔧 **{tool_name}**", expanded=False):
                if is_error:
                    st.error("Tool executed with error")
                else:
                    st.success("Tool executed successfully")

                # Show tool ID if available
                if tool_id:
                    st.caption(f"Tool ID: `{tool_id}`")

                # Show tool input parameters
                if tool_input:
                    st.caption("Parameters:")
                    # Use st.json for nice formatting of the input parameters
                    st.json(tool_input)
                else:
                    st.info("No parameters provided")

                # Show tool result
                st.caption("Result:")

                if tool_content:
                    # Try to display content in a user-friendly way
                    if isinstance(tool_content, (dict, list)):
                        st.json(tool_content)
                    else:
                        # Display as code block for better formatting
                        st.code(str(tool_content), language="text")
                else:
                    st.info("No result content")

                # Show result ID if different from tool use ID
                if tool_result_id and tool_result_id != tool_id:
                    st.caption(f"Result ID: `{tool_result_id}`")

        except Exception as e:
            # Fallback rendering in case of any errors
            st.error(f"Error rendering tool use: {str(e)}")
            st.json({"tool_use": tool_use_block, "tool_result": tool_result_block})


class ToolCallback(object):
    def __init__(self, placeholder):
        self.tool_calls: List[ToolTrace] = [ToolTrace()]
        self.placeholder = placeholder

    def __call__(self, message: ToolUse | ToolResult):
        trace = self.tool_calls[-1]
        if trace.is_complete:
            trace = ToolTrace()
            self.tool_calls.append(trace)

        if "toolUse" in message:
            trace.begin(message["toolUse"])
        elif "toolResult" in message:
            trace.end(message["toolResult"])

        with self.placeholder:
            for call in self.tool_calls:
                call.render(clear=False)


class StreamCallback(object):
    def __init__(self, placeholder):
        self.tool_trace = ToolTrace()
        self.text = ""
        self.placeholder = placeholder

    def rerender(self):
        with self.placeholder:
            if self.tool_trace.is_complete:
                self.tool_trace.render(clear=False)
            self.placeholder.markdown(self.text)

    def on_tool(self, message: ToolUse | ToolResult):
        if "toolUse" in message:
            self.tool_trace.begin(message["toolUse"])
        elif "toolResult" in message:
            self.tool_trace.end(message["toolResult"])
        self.rerender()

    def __call__(self, data: str):
        self.text += data
        self.placeholder.markdown(self.text)


def render_message(message: SessionMessage, tool_trace: ToolTrace):
    msg = message.to_message()
    msg_role = msg["role"]
    msg_content = msg["content"]

    for block in msg_content:
        if "text" in block:
            with st.chat_message(msg_role):
                if tool_trace.is_complete:
                    tool_trace.render()
                st.markdown(block["text"])

        if "toolUse" in block:
            tool_trace.begin(block["toolUse"])

        if "toolResult" in block:
            tool_trace.end(block["toolResult"])


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

    trace = ToolTrace()
    for msg in chat_session.get_history():
        render_message(msg, trace)

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

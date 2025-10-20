# import re

import streamlit as st
from strands.types.content import Message
from streamlit.delta_generator import DeltaGenerator

from fivcadvisor.agents.types import AgentsRuntime, AgentsRuntimeToolCall


class ChatMessage(object):
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
<span class='loading-dots'></span>
"""

    def __init__(self, runtime: AgentsRuntime):
        self.runtime = runtime

    def render(self, placeholder: DeltaGenerator):
        placeholder = placeholder.container()

        if self.runtime.query:
            c = placeholder.chat_message("user")
            c.text(self.runtime.query)

        c = placeholder.chat_message("assistant")

        # Render tool calls if any
        if self.runtime.tool_calls:
            for tool_call in self.runtime.tool_calls.values():
                self.render_tool_call(tool_call, c)

        # Render message or streaming text
        if self.runtime.reply:
            self.render_message(self.runtime.reply, c)
        else:
            self.render_streaming(self.runtime.streaming_text, c)

    @staticmethod
    def render_message(
        message: Message,
        placeholder: DeltaGenerator,
    ):
        msg = message
        # msg_role = msg["role"]
        msg_content = msg["content"]

        for msg_block in msg_content:
            if "text" in msg_block:
                msg_block_text = msg_block["text"]
                # msg_block_text = thinking_prettify(msg_block_text)
                placeholder.markdown(msg_block_text, unsafe_allow_html=True)

    @staticmethod
    def render_tool_call(
        tool_call: AgentsRuntimeToolCall,
        placeholder: DeltaGenerator,
    ):
        try:
            tool_name = tool_call.tool_name
            tool_id = tool_call.tool_use_id
            tool_input = tool_call.tool_input
            tool_result = tool_call.tool_result
            status = tool_call.status

            # Create an expander with the tool name and a tool icon
            with placeholder.expander(f"🔧 **{tool_name}**", expanded=False):
                # Show status
                is_error = status == "error"
                if is_error:
                    st.error("Tool executed with error")
                    if tool_call.error:
                        st.error(f"Error: {tool_call.error}")
                elif status == "success":
                    st.success("Tool executed successfully")
                else:
                    st.info("Tool execution pending...")

                # Show tool ID if available
                if tool_id:
                    st.caption(f"Tool ID: `{tool_id}`")

                # Show timing information if available
                if tool_call.duration is not None:
                    st.caption(f"Duration: {tool_call.duration:.3f}s")

                # Show tool input parameters
                if tool_input:
                    st.caption("Parameters:")
                    # Use st.json for nice formatting of the input parameters
                    st.json(tool_input)
                else:
                    st.info("No parameters provided")

                # Show tool result if available
                if tool_result is not None:
                    st.caption("Result:")

                    if isinstance(tool_result, (dict, list)):
                        st.json(tool_result)
                    else:
                        # Display as code block for better formatting
                        st.code(str(tool_result), language="text")
                elif status != "pending":
                    st.info("No result content")

        except Exception as e:
            # Fallback rendering in case of any errors
            st.error(f"Error rendering tool call: {str(e)}")
            st.json(tool_call.model_dump())

    def render_streaming(
        self,
        streaming: str,
        placeholder: DeltaGenerator,
    ):
        streaming_text = streaming
        streaming_text = f"{streaming_text}{self.loading_indicator}"
        placeholder.markdown(streaming_text, unsafe_allow_html=True)

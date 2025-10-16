import re
from typing import Optional

import streamlit as st
from strands.types.content import Message
from streamlit.delta_generator import DeltaGenerator

from fivcadvisor.agents.types import AgentsRuntime, AgentsRuntimeToolCall


def render(runtime: AgentsRuntime, placeholder: DeltaGenerator):
    """
    Render a chat message from an AgentsRuntime.

    Displays both user query and assistant response. The assistant response
    can be either a completed message or streaming text, depending on the
    runtime state. Also renders tool calls from runtime.tool_calls.

    Args:
        placeholder: Streamlit container to render into
        runtime: AgentsRuntime containing query, message, tool_calls, or streaming_text

    The function handles three states:
    - User query: Rendered as a user chat message
    - Completed message: Rendered with full message content
    - Streaming: Rendered with animated loading indicator
    - Tool calls: Rendered in expandable sections
    """
    placeholder = placeholder.container()

    if runtime.query:
        c = placeholder.chat_message("user")
        c.text(runtime.query)

    c = placeholder.chat_message("assistant")

    # Render tool calls if any
    if runtime.tool_calls:
        for tool_call in runtime.tool_calls.values():
            tool_call_render(tool_call, c)

    # Render message or streaming text
    if runtime.reply:
        message_render(runtime.reply, c)
    else:
        streaming_render(runtime.streaming_text, c)


def message_render(message: Message, placeholder: Optional[DeltaGenerator]):
    """
    Render a completed message with formatted content.

    Processes message content blocks and applies special formatting
    for <think> tags using thinking_prettify().

    Args:
        placeholder: Streamlit container to render into
        message: Message dict with role and content blocks

    Content blocks with "text" keys are rendered as markdown with
    HTML support for styled think sections.
    """
    msg = message
    # msg_role = msg["role"]
    msg_content = msg["content"]

    for msg_block in msg_content:
        if "text" in msg_block:
            msg_block_text = msg_block["text"]
            msg_block_text = thinking_prettify(msg_block_text)
            placeholder.markdown(msg_block_text, unsafe_allow_html=True)


streaming_indicator = """
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


def streaming_render(streaming_text: str, placeholder: DeltaGenerator):
    """
    Render streaming text with animated loading indicator.

    Displays the current streaming text with a pulsing dots animation
    to indicate that the response is still being generated.

    Args:
        placeholder: Streamlit container to render into
        streaming_text: Current accumulated streaming text

    The loading indicator uses CSS animations for a smooth visual effect.
    Think tags in streaming text are also processed for consistent styling.
    """
    streaming_text = thinking_prettify(streaming_text)
    streaming_text = (
        f"{streaming_indicator}{streaming_text}<span class='loading-dots'></span>"
    )
    placeholder.markdown(streaming_text, unsafe_allow_html=True)


# CSS styles for think blocks
thinking_style = """
<style>
.think-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
    border-left: 4px solid #667eea;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
}
.think-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #667eea;
    margin-bottom: 10px;
    font-size: 0.95em;
    letter-spacing: 0.5px;
}
.think-icon {
    font-size: 1.2em;
    animation: pulse-think 2s ease-in-out infinite;
}
.think-content {
    color: #4a5568;
    line-height: 1.6;
    font-size: 0.9em;
    white-space: pre-wrap;
    word-wrap: break-word;
}
@keyframes pulse-think {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.7;
        transform: scale(1.1);
    }
}
</style>
"""


def thinking_replace(message_text):
    # Pattern to match <think>...</think> tags (including multiline content)
    def _replace(match):
        content = match.group(1).strip()
        return f"""
            <div class="think-container">
                <div class="think-header">
                    <span class="think-icon">🤔</span>
                    <span>Thinking...</span>
                </div>
                <div class="think-content">{content}</div>
            </div>
            """

    # Replace all think tags with styled HTML
    message_text = re.sub(
        r"<think>(.*?)</think>", _replace, message_text, flags=re.DOTALL
    )
    return thinking_style + message_text


def thinking_prettify(message_text: str) -> str:
    """
    Process <think></think> tags in the text and apply styling.

    Args:
        message_text: The text containing potential <think> tags

    Returns:
        Processed text with styled think sections
    """

    # Add the style if we found any think tags
    if "<think>" in message_text:
        message_text = thinking_replace(message_text)

    return message_text


def tool_call_render(tool_call: AgentsRuntimeToolCall, placeholder: DeltaGenerator):
    """
    Render a tool call with its result in an expander.

    Displays tool invocation details and results in a user-friendly expandable format,
    including status indicators, timing information, input parameters, and results.

    Args:
        tool_call: AgentsRuntimeToolCall containing tool invocation and result
        placeholder: Streamlit container to render into
    """
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

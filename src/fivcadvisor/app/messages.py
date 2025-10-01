import re
from typing import List, Optional

import streamlit as st
from strands.types.content import Message
from strands.types.session import SessionMessage
from fivcadvisor.app.tools import ToolsRenderer


def process_think_tags(text: str) -> str:
    """
    Process <think></think> tags in the text and apply styling.

    Args:
        text: The text containing potential <think> tags

    Returns:
        Processed text with styled think sections
    """
    # CSS styles for think blocks
    think_style = """
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

    # Pattern to match <think>...</think> tags (including multiline content)
    pattern = r"<think>(.*?)</think>"

    def replace_think(match):
        content = match.group(1).strip()
        return f"""
        <div class="think-container">
            <div class="think-header">
                <span class="think-icon">🤔</span>
                <span>模型思考中...</span>
            </div>
            <div class="think-content">{content}</div>
        </div>
        """

    # Replace all think tags with styled HTML
    processed_text = re.sub(pattern, replace_think, text, flags=re.DOTALL)

    # Add the style if we found any think tags
    if "<think>" in text:
        processed_text = think_style + processed_text

    return processed_text


class MessagesRenderer(object):
    def __init__(self, messages: List[SessionMessage]):
        self.messages = messages
        self.tool_traces = ToolsRenderer()

    def render(self):
        for message in self.messages:
            self.render_message(message.to_message())

    def render_message(self, message: Message):
        msg = message
        msg_role = msg["role"]
        msg_content = msg["content"]

        # First pass: process all tool use and result blocks
        for block in msg_content:
            if "text" in block:
                with st.chat_message(msg_role):
                    # Process think tags in the text before rendering
                    processed_text = process_think_tags(block["text"])
                    st.markdown(processed_text, unsafe_allow_html=True)

            if "toolUse" in block:
                self.tool_traces.begin(block["toolUse"])

            if "toolResult" in block:
                self.tool_traces.end(block["toolResult"])

        self.tool_traces.render()


class MessageCallback(object):
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
        # Process think tags in the text
        processed_text = process_think_tags(self.text)
        # Display text with animated loading dots
        text_with_loading = f"{processed_text}<span class='loading-dots'></span>"
        self.placeholder.markdown(
            self.loading_indicator + text_with_loading, unsafe_allow_html=True
        )

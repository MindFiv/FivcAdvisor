"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
"""

__all__ = [
    "create_default_ui",
    "main",
]

import streamlit as st
import time

from fivcadvisor import agents, tools
from fivcadvisor.app.sessions import (
    Session,
    SessionExecutionStatus,
)
from fivcadvisor.app.components import (
    ChatBox,
    ChatInput,
    ConfigPanel,
)


def create_default_ui():
    """Create the Streamlit interface."""

    # Initialize session state
    session = Session(
        agents_retriever=agents.default_retriever,
        tools_retriever=tools.default_retriever,
    )
    # Initialize components
    chat_box = ChatBox(session)
    chat_input = ChatInput(session)
    config_panel = ConfigPanel(session)

    # Page configuration
    st.set_page_config(
        page_title="FivcAdvisor - Intelligent Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Sidebar
    with st.sidebar:
        config_panel.render()

    # Main area
    chat_input.render()
    chat_box.render()

    # Run the session
    session.run()

    # Auto-refresh when agent is running
    if session.execution_status == SessionExecutionStatus.RUNNING:
        time.sleep(1)  # Wait 1 second before next refresh
        st.rerun()


def main():
    """Main Streamlit application entry point."""
    create_default_ui()


if __name__ == "__main__":
    main()

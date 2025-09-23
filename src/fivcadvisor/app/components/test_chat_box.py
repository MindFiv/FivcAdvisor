"""
Test script for ChatBox

This script demonstrates how to use the ChatBox independently with the new ChatMessage component.
"""

import streamlit as st
from chat_box import create_default_chat_box


def mock_process_message(message: str, graph_type: str, verbose: bool):
    """Mock message processing function for testing."""
    # Simulate different types of responses for testing
    if "reasoning" in message.lower():
        return {
            "type": "structured",
            "content": f"Mock answer for: '{message}' using {graph_type} graph",
            "answer": f"Mock answer for: '{message}' using {graph_type} graph",
            "reasoning": f"This is the reasoning process:\n1. Analyzed the query: '{message}'\n2. Selected graph type: {graph_type}\n3. Verbose mode: {verbose}\n4. Generated appropriate response",
        }
    else:
        return {
            "type": "simple",
            "content": f"Mock response to: '{message}' (Graph: {graph_type}, Verbose: {verbose})",
            "answer": None,
            "reasoning": None,
        }


def mock_get_example_queries():
    """Mock example queries function for testing."""
    return [
        "What is machine learning with reasoning?",
        "Write a Python function with reasoning",
        "Simple query without reasoning",
        "Explain quantum computing with reasoning",
    ]


def test_chat_box():
    """Test the chat box in isolation."""
    st.set_page_config(
        page_title="Chat Box Test",
        page_icon="🧪",
        layout="wide",
    )

    st.title("🧪 Chat Box Test")
    st.markdown("Testing the ChatBox in isolation")
    st.markdown("---")

    # Initialize session state for testing
    if "test_graph_type" not in st.session_state:
        st.session_state.test_graph_type = "general"
    if "test_verbose" not in st.session_state:
        st.session_state.test_verbose = False

    # Create chat box
    chat_box = create_default_chat_box(
        process_message_callback=mock_process_message,
        get_example_queries_callback=mock_get_example_queries,
    )

    # Sidebar for testing controls
    with st.sidebar:
        st.header("🔧 Test Controls")

        st.session_state.test_graph_type = st.selectbox(
            "Graph Type",
            ["general", "simple", "complex"],
            index=0,
        )

        st.session_state.test_verbose = st.checkbox(
            "Verbose Mode",
            value=st.session_state.test_verbose,
        )

        st.markdown("---")

        # Chat box sidebar elements
        chat_box.render_sidebar_components(
            st.session_state.test_graph_type, st.session_state.test_verbose
        )

    # Main chat interface
    chat_box.render_full_chat_interface(
        st.session_state.test_graph_type,
        st.session_state.test_verbose,
        title="💬 Test Chat Interface",
    )


if __name__ == "__main__":
    test_chat_box()

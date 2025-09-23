"""
Test script for SideBar Component

This script demonstrates how to use the SideBar component independently.
"""

import streamlit as st
from side_bar import (
    SideBar,
    # ChatSideBar,
    create_default_sidebar,
    create_chat_sidebar,
)


def mock_clear_chat():
    """Mock function to clear chat."""
    st.session_state.test_messages = []
    st.success("Chat cleared!")


def mock_get_example_queries():
    """Mock function to get example queries."""
    return [
        "What is machine learning?",
        "Explain neural networks",
        "How does deep learning work?",
        "What are the types of AI?",
        "Describe natural language processing",
        "What is computer vision?",
    ]


def mock_handle_example_query(query: str, graph_type: str, verbose: bool):
    """Mock function to handle example query selection."""
    if "test_messages" not in st.session_state:
        st.session_state.test_messages = []

    st.session_state.test_messages.append(
        {
            "role": "user",
            "content": query,
            "graph_type": graph_type,
            "verbose": verbose,
        }
    )
    st.success(f"Added query: {query}")
    st.rerun()


def get_mock_available_graphs():
    """Get mock available graphs for testing."""
    return {
        "simple": "A simple linear processing graph for basic tasks",
        "complex": "A complex multi-agent graph for advanced reasoning",
        "research": "A specialized graph for research and analysis tasks",
        "creative": "A creative graph optimized for content generation",
    }


def test_basic_sidebar():
    """Test basic sidebar functionality."""
    st.header("🧪 Basic SideBar Test")

    # Initialize session state
    if "basic_graph_type" not in st.session_state:
        st.session_state.basic_graph_type = "simple"
    if "basic_verbose" not in st.session_state:
        st.session_state.basic_verbose = False

    # Create sidebar
    sidebar = create_default_sidebar("basic_test")

    # Custom section function
    def custom_section():
        st.subheader("🎨 Custom Section")
        st.info("This is a custom section added to the sidebar!")
        if st.button("Custom Action", key="custom_action"):
            st.success("Custom action executed!")

    # Render sidebar
    config = sidebar.render(
        available_graphs=get_mock_available_graphs(),
        current_graph_type=st.session_state.basic_graph_type,
        current_verbose=st.session_state.basic_verbose,
        clear_chat_callback=mock_clear_chat,
        example_queries_callback=mock_get_example_queries,
        handle_example_query_callback=mock_handle_example_query,
        show_examples=True,
        max_examples=3,
        custom_sections=[custom_section],
    )

    # Update session state
    st.session_state.basic_graph_type = config["graph_type"]
    st.session_state.basic_verbose = config["verbose"]

    # Display current configuration
    st.subheader("📊 Current Configuration")
    st.json(
        {
            "graph_type": config["graph_type"],
            "verbose": config["verbose"],
        }
    )

    # Display test messages
    if "test_messages" in st.session_state and st.session_state.test_messages:
        st.subheader("📝 Test Messages")
        for i, msg in enumerate(st.session_state.test_messages):
            with st.expander(f"Message {i+1}: {msg['content'][:30]}..."):
                st.json(msg)


def test_chat_sidebar():
    """Test chat-specific sidebar functionality."""
    st.header("💬 ChatSideBar Test")

    # Initialize session state
    if "chat_graph_type" not in st.session_state:
        st.session_state.chat_graph_type = "complex"
    if "chat_verbose" not in st.session_state:
        st.session_state.chat_verbose = True

    # Create chat sidebar
    chat_sidebar = create_chat_sidebar("chat_test")

    # Mock ChatBox class for testing
    class MockChatBox:
        def clear_chat(self):
            mock_clear_chat()

        def get_example_queries_callback(self):
            return mock_get_example_queries()

        def _handle_example_query(self, query: str, graph_type: str, verbose: bool):
            mock_handle_example_query(query, graph_type, verbose)

    mock_chat_box = MockChatBox()

    # Render chat sidebar
    config = chat_sidebar.render_for_chat_box(
        available_graphs=get_mock_available_graphs(),
        current_graph_type=st.session_state.chat_graph_type,
        current_verbose=st.session_state.chat_verbose,
        chat_box=mock_chat_box,
        show_examples=True,
        max_examples=4,
    )

    # Update session state
    st.session_state.chat_graph_type = config["graph_type"]
    st.session_state.chat_verbose = config["verbose"]

    # Display current configuration
    st.subheader("📊 Chat Configuration")
    st.json(
        {
            "graph_type": config["graph_type"],
            "verbose": config["verbose"],
        }
    )


def test_sidebar_customization():
    """Test sidebar customization options."""
    st.header("🎨 SideBar Customization Test")

    # Initialize session state
    if "custom_graph_type" not in st.session_state:
        st.session_state.custom_graph_type = "research"
    if "custom_verbose" not in st.session_state:
        st.session_state.custom_verbose = False

    # Create customized sidebar
    sidebar = SideBar(
        session_key_prefix="custom_test",
        title="🔧 Custom Configuration",
        show_graph_info=True,
        show_chat_controls=True,
    )

    # Multiple custom sections
    def analytics_section():
        st.subheader("📈 Analytics")
        st.metric("Total Queries", len(st.session_state.get("test_messages", [])))
        st.metric("Graph Changes", st.session_state.get("graph_changes", 0))

    def settings_section():
        st.subheader("⚙️ Advanced Settings")
        if st.checkbox("Enable Debug Mode", key="debug_mode"):
            st.info("Debug mode enabled!")

        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, key="temperature")
        st.write(f"Temperature: {temperature}")

    # Render customized sidebar
    config = sidebar.render(
        available_graphs=get_mock_available_graphs(),
        current_graph_type=st.session_state.custom_graph_type,
        current_verbose=st.session_state.custom_verbose,
        clear_chat_callback=mock_clear_chat,
        example_queries_callback=mock_get_example_queries,
        handle_example_query_callback=mock_handle_example_query,
        show_examples=True,
        max_examples=5,
        custom_sections=[analytics_section, settings_section],
    )

    # Track graph changes
    if config["graph_type"] != st.session_state.custom_graph_type:
        st.session_state.graph_changes = st.session_state.get("graph_changes", 0) + 1

    # Update session state
    st.session_state.custom_graph_type = config["graph_type"]
    st.session_state.custom_verbose = config["verbose"]

    # Display current configuration
    st.subheader("📊 Custom Configuration")
    st.json(
        {
            "graph_type": config["graph_type"],
            "verbose": config["verbose"],
            "debug_mode": st.session_state.get("debug_mode", False),
            "temperature": st.session_state.get("temperature", 0.7),
            "graph_changes": st.session_state.get("graph_changes", 0),
        }
    )


def main():
    """Main test application."""
    st.set_page_config(
        page_title="SideBar Component Test",
        page_icon="🎛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🎛️ SideBar Component Test")
    st.markdown("Testing the SideBar component and its various configurations")
    st.markdown("---")

    # Test mode selection
    test_mode = st.selectbox(
        "Select Test Mode",
        [
            "Basic SideBar",
            "Chat SideBar",
            "Customization Test",
            "All Tests",
        ],
        help="Choose which sidebar test to run",
    )

    # Run selected tests
    if test_mode == "All Tests":
        test_basic_sidebar()
        st.markdown("---")
        test_chat_sidebar()
        st.markdown("---")
        test_sidebar_customization()
    elif test_mode == "Basic SideBar":
        test_basic_sidebar()
    elif test_mode == "Chat SideBar":
        test_chat_sidebar()
    elif test_mode == "Customization Test":
        test_sidebar_customization()

    # Footer
    st.markdown("---")
    st.markdown(
        "**Note:** This test demonstrates the SideBar component functionality. The sidebar controls should appear on the left side of the screen."
    )


if __name__ == "__main__":
    main()

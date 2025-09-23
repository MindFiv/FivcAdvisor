"""
Test script for ChatMessage Component

This script demonstrates how to use the ChatMessage component independently.
"""

import streamlit as st
from chat_message import (
    ChatMessage,
    # ChatMessageRenderer,
    create_chat_message_renderer,
    format_user_message,
    format_assistant_message,
    format_error_message,
    format_structured_response,
)


def create_test_messages():
    """Create various test messages to demonstrate different message types."""
    return [
        # User message
        format_user_message("Hello, can you explain machine learning?"),
        # Simple assistant response
        format_assistant_message(
            "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."
        ),
        # User message asking for reasoning
        format_user_message("Can you explain that with your reasoning process?"),
        # Structured response with reasoning
        format_assistant_message(
            content="Machine learning is a method of data analysis that automates analytical model building. It's based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention.",
            reasoning="""Here's my thought process:

1. **Definition Analysis**: I started with the core concept - ML as a subset of AI
2. **Key Characteristics**: Focused on the automation and learning aspects
3. **Learning Mechanism**: Emphasized learning from data rather than explicit programming
4. **Pattern Recognition**: Highlighted the ability to identify patterns
5. **Decision Making**: Mentioned autonomous decision-making capabilities
6. **Human Intervention**: Noted the minimal human involvement required

This explanation covers the fundamental aspects while being accessible to beginners.""",
        ),
        # User message that might cause an error
        format_user_message("What happens when there's an error?"),
        # Error message
        format_error_message(
            "This is a simulated error message to show error formatting."
        ),
        # User message asking about complex topic
        format_user_message("Tell me about neural networks with detailed reasoning"),
        # Complex structured response
        format_structured_response(
            {
                "type": "structured",
                "content": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information through weighted connections, learning patterns through training on data.",
                "answer": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information through weighted connections, learning patterns through training on data.",
                "reasoning": """My reasoning for this explanation:

**Conceptual Foundation:**
- Started with the biological inspiration to provide context
- Explained the basic structure (nodes/neurons)
- Described the connection mechanism (weighted connections)

**Learning Process:**
- Emphasized the pattern learning capability
- Mentioned training as the key learning mechanism
- Connected data to the learning process

**Technical Accuracy:**
- Used precise terminology (nodes, neurons, weighted connections)
- Avoided overly complex mathematical details
- Focused on conceptual understanding

**Pedagogical Approach:**
- Built from familiar concepts (biological networks)
- Progressed to technical implementation
- Maintained accessibility for general audience

This explanation balances technical accuracy with understandability.""",
            }
        ),
    ]


def test_individual_components():
    """Test individual message components."""
    st.header("🧪 Individual Component Tests")

    # Test ChatMessage component
    st.subheader("ChatMessage Component")
    message_component = ChatMessage("test_individual")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Simple Message:**")
        simple_msg = format_assistant_message(
            "This is a simple message without reasoning."
        )
        message_component.render(simple_msg, 0)

    with col2:
        st.write("**Structured Message:**")
        structured_msg = format_assistant_message(
            "This is a structured message with reasoning.",
            "This reasoning explains why this message was structured this way.",
        )
        message_component.render(structured_msg, 1)


def test_message_renderer():
    """Test the ChatMessageRenderer with multiple messages."""
    st.header("💬 Message Renderer Test")

    renderer = create_chat_message_renderer("test_renderer")
    test_messages = create_test_messages()

    st.write(f"Rendering {len(test_messages)} test messages:")
    renderer.render_messages(test_messages)


def test_utility_functions():
    """Test utility functions for message formatting."""
    st.header("🔧 Utility Functions Test")

    st.subheader("Message Formatting Functions")

    # Test format_user_message
    st.write("**User Message Formatting:**")
    user_msg = format_user_message("Test user message")
    st.json(user_msg)

    # Test format_assistant_message
    st.write("**Assistant Message Formatting:**")
    assistant_msg = format_assistant_message("Test assistant message", "Test reasoning")
    st.json(assistant_msg)

    # Test format_error_message
    st.write("**Error Message Formatting:**")
    error_msg = format_error_message("Test error occurred")
    st.json(error_msg)

    # Test format_structured_response
    st.write("**Structured Response Formatting:**")
    structured_response = format_structured_response(
        {"answer": "Test answer", "reasoning": "Test reasoning", "type": "structured"}
    )
    st.json(structured_response)


def main():
    """Main test application."""
    st.set_page_config(
        page_title="Chat Message Component Test",
        page_icon="💬",
        layout="wide",
    )

    st.title("💬 Chat Message Component Test")
    st.markdown("Testing the ChatMessage component and related utilities")
    st.markdown("---")

    # Sidebar for test selection
    with st.sidebar:
        st.header("🎛️ Test Options")

        test_mode = st.selectbox(
            "Select Test Mode",
            [
                "All Tests",
                "Message Renderer",
                "Individual Components",
                "Utility Functions",
            ],
        )

        st.markdown("---")
        st.markdown("**Test Description:**")
        if test_mode == "All Tests":
            st.info("Run all available tests to see the complete functionality.")
        elif test_mode == "Message Renderer":
            st.info("Test the ChatMessageRenderer with various message types.")
        elif test_mode == "Individual Components":
            st.info("Test individual ChatMessage components in isolation.")
        elif test_mode == "Utility Functions":
            st.info("Test utility functions for message formatting.")

    # Run selected tests
    if test_mode == "All Tests":
        test_message_renderer()
        st.markdown("---")
        test_individual_components()
        st.markdown("---")
        test_utility_functions()
    elif test_mode == "Message Renderer":
        test_message_renderer()
    elif test_mode == "Individual Components":
        test_individual_components()
    elif test_mode == "Utility Functions":
        test_utility_functions()


if __name__ == "__main__":
    main()

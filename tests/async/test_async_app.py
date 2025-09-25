#!/usr/bin/env python3
"""
Test script for the async-optimized FivcAdvisor app.
This script demonstrates the non-blocking agent execution.
"""

import sys
import os
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_async_execution():
    """Test the async execution functionality."""
    print("Testing async execution functionality...")

    # Import after path setup
    from fivcadvisor.app.sessions import Session, SessionData, SessionExecutionStatus
    from fivcadvisor import graphs, tools

    # Create a mock streamlit session state
    class MockSessionState:
        def __init__(self):
            self.session_data = SessionData()

    # Mock streamlit
    import streamlit as st

    st.session_state = MockSessionState()

    # Create session
    session = Session(
        graph_retriever=graphs.default_retriever,
        tools_retriever=tools.default_retriever,
    )

    print("✓ Session created successfully")

    # Test asking a question
    test_query = "What is machine learning?"
    print(f"Asking: {test_query}")

    session.ask(test_query)
    print("✓ Question asked (non-blocking)")

    # Simulate the run cycle
    print("Starting execution...")
    session.run()

    # Monitor execution status
    start_time = time.time()
    while session.execution_status == SessionExecutionStatus.RUNNING:
        print(f"Status: {session.execution_status.value} - {session.progress_message}")
        time.sleep(1)

        # Simulate checking status (like Streamlit would do)
        session._check_execution_status()

        # Timeout after 30 seconds for testing
        if time.time() - start_time > 30:
            print("Timeout reached, cancelling execution...")
            session.cancel_execution()
            break

    print(f"Final status: {session.execution_status.value}")
    print(f"Messages count: {len(session.get_messages())}")

    # Print messages
    for i, msg in enumerate(session.get_messages()):
        print(f"Message {i+1} ({msg.role}): {msg.content[:100]}...")

    print("✓ Test completed")


if __name__ == "__main__":
    test_async_execution()

"""
FivcAdvisor Streamlit Web Application

A modern, interactive Streamlit interface for FivcAdvisor with Agent chat functionality.
"""

from typing import Dict, Any, List
from uuid import uuid4
import asyncio
import json

import streamlit as st

from fivcadvisor.graphs import (
    create_general_graph,
    create_simple_graph,
    create_complex_graph,
)
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)
from fivcadvisor.utils import create_output_dir

__version__ = "0.1.0"


def get_available_graphs() -> Dict[str, str]:
    """Get available graph types and their descriptions."""
    return {
        "general": "Intelligent task complexity assessment and execution",
        "simple": "Simple task execution with basic crew",
        "complex": "Complex task execution with advanced planning",
    }


async def run_graph_async(
    graph_type: str, query: str, verbose: bool = False
) -> Dict[str, Any]:
    """Run a graph asynchronously and return the result."""
    try:
        # Create tools retriever and register tools
        tools_retriever = create_retriever()

        with create_output_dir():
            register_default_tools(tools_retriever=tools_retriever)
            register_mcp_tools(tools_retriever=tools_retriever)

            # Create the appropriate graph
            if graph_type == "general":
                graph = create_general_graph()
            elif graph_type == "simple":
                graph = create_simple_graph()
            elif graph_type == "complex":
                graph = create_complex_graph()
            else:
                return {
                    "success": False,
                    "error": f"Unknown graph type: {graph_type}",
                    "result": None,
                }

            # Create graph run instance
            graph_run = graph(
                tools_retriever=tools_retriever,
                verbose=verbose,
                session_id=str(uuid4()),
            )

            # Execute the graph
            result = await graph_run.kickoff_async(inputs={"user_query": query})

            return {
                "success": True,
                "error": None,
                "result": result,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": None,
        }


def run_graph_sync(
    graph_type: str, query: str, verbose: bool = False
) -> Dict[str, Any]:
    """Run a graph synchronously by wrapping the async function."""
    return asyncio.run(run_graph_async(graph_type, query, verbose))


def format_result(result: Dict[str, Any]) -> str:
    """Format the result for display in chat."""
    if not result["success"]:
        return f"❌ **Error:** {result['error']}"

    if not result["result"]:
        return "✅ Query processed successfully, but no result returned."

    # Try to extract the final result nicely
    final_result = result["result"].get("final_result")
    if final_result:
        if isinstance(final_result, dict):
            if "final_output" in final_result:
                return f"✅ **Result:**\n\n{final_result['final_output']}"
            else:
                return f"✅ **Result:**\n\n```json\n{json.dumps(final_result, indent=2)}\n```"
        else:
            return f"✅ **Result:**\n\n{final_result}"
    else:
        return (
            f"✅ **Result:**\n\n```json\n{json.dumps(result['result'], indent=2)}\n```"
        )


def process_message(message: str, graph_type: str, verbose: bool) -> str:
    """Process a user message and return the response."""
    if not message.strip():
        return "Please enter a message."

    # Process the query
    result = run_graph_sync(graph_type, message.strip(), verbose)

    # Format the response
    response = format_result(result)
    return response


def get_example_queries() -> List[str]:
    """Get example queries for the interface."""
    return [
        "What is machine learning?",
        "Write a Python function to calculate fibonacci numbers",
        "Explain the benefits of renewable energy",
        "Create a simple web scraping script",
        "What are the latest trends in AI?",
        "Help me understand how neural networks work",
        "Generate a simple REST API example",
        "Explain quantum computing basics",
    ]


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "graph_type" not in st.session_state:
        st.session_state.graph_type = "general"
    if "verbose" not in st.session_state:
        st.session_state.verbose = False


def create_interface():
    """Create the Streamlit interface."""
    # Page configuration
    st.set_page_config(
        page_title="FivcAdvisor - Intelligent Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    initialize_session_state()

    # Header
    st.title("🤖 FivcAdvisor")
    st.markdown(
        "*Intelligent Multi-Agent Task Processing with Advanced Graph Orchestration*"
    )
    st.markdown("---")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        available_graphs = get_available_graphs()

        # Graph type selection
        graph_options = [(f"{k.title()} - {v}", k) for k, v in available_graphs.items()]
        graph_labels = [option[0] for option in graph_options]
        graph_values = [option[1] for option in graph_options]

        selected_index = 0
        if st.session_state.graph_type in graph_values:
            selected_index = graph_values.index(st.session_state.graph_type)

        selected_label = st.selectbox(
            "Graph Type",
            graph_labels,
            index=selected_index,
            help="Select the processing strategy",
        )
        st.session_state.graph_type = graph_values[graph_labels.index(selected_label)]

        # Verbose mode
        st.session_state.verbose = st.checkbox(
            "Verbose Mode",
            value=st.session_state.verbose,
            help="Show detailed processing information",
        )

        st.markdown("---")

        # Graph information
        st.subheader("📊 Graph Information")
        st.info(
            f"**{st.session_state.graph_type.title()} Graph**\n\n{available_graphs[st.session_state.graph_type]}"
        )

        st.markdown("---")

        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        # Example queries
        st.subheader("💡 Example Queries")
        example_queries = get_example_queries()

        for i, query in enumerate(example_queries[:4]):  # Show first 4 examples
            if st.button(
                f"📝 {query[:30]}...", key=f"example_{i}", use_container_width=True
            ):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.spinner("Processing..."):
                    response = process_message(
                        query, st.session_state.graph_type, st.session_state.verbose
                    )
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

    # Main chat interface
    st.subheader("💬 Chat with FivcAdvisor")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                response = process_message(
                    prompt, st.session_state.graph_type, st.session_state.verbose
                )
            st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


def main():
    """Main Streamlit application entry point."""
    create_interface()


if __name__ == "__main__":
    main()


# Export functions for compatibility
__all__ = [
    "main",
    "create_interface",
    "get_available_graphs",
    "run_graph_sync",
    "run_graph_async",
]

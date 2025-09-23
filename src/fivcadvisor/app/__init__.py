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
from fivcadvisor.app.components import create_default_chat_box, create_chat_sidebar

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


def format_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format the result for display in chat, returning structured data."""
    if not result["success"]:
        return {
            "type": "error",
            "content": f"❌ **Error:** {result['error']}",
            "answer": None,
            "reasoning": None,
        }

    if not result["result"]:
        return {
            "type": "simple",
            "content": "✅ Query processed successfully, but no result returned.",
            "answer": None,
            "reasoning": None,
        }

    # Try to extract the final result nicely
    final_result = result["result"].get("final_result")
    if final_result:
        if isinstance(final_result, dict):
            # Check if it has answer and reasoning fields (structured response)
            if "answer" in final_result and "reasoning" in final_result:
                return {
                    "type": "structured",
                    "content": final_result["answer"],
                    "answer": final_result["answer"],
                    "reasoning": final_result["reasoning"],
                }
            elif "final_output" in final_result:
                return {
                    "type": "simple",
                    "content": f"✅ **Result:**\n\n{final_result['final_output']}",
                    "answer": None,
                    "reasoning": None,
                }
            else:
                # Try to parse as JSON string if it looks like one
                json_content = json.dumps(final_result, indent=2)
                parsed_data = _try_parse_agent_response(json_content)
                if parsed_data:
                    return {
                        "type": "structured",
                        "content": parsed_data["answer"],
                        "answer": parsed_data["answer"],
                        "reasoning": parsed_data["reasoning"],
                    }
                else:
                    return {
                        "type": "simple",
                        "content": f"✅ **Result:**\n\n```json\n{json_content}\n```",
                        "answer": None,
                        "reasoning": None,
                    }
        else:
            # Try to parse the string result as JSON
            parsed_data = _try_parse_agent_response(str(final_result))
            if parsed_data:
                return {
                    "type": "structured",
                    "content": parsed_data["answer"],
                    "answer": parsed_data["answer"],
                    "reasoning": parsed_data["reasoning"],
                }
            else:
                return {
                    "type": "simple",
                    "content": f"✅ **Result:**\n\n{final_result}",
                    "answer": None,
                    "reasoning": None,
                }
    else:
        # Try to parse the entire result as JSON
        json_content = json.dumps(result["result"], indent=2)
        parsed_data = _try_parse_agent_response(json_content)
        if parsed_data:
            return {
                "type": "structured",
                "content": parsed_data["answer"],
                "answer": parsed_data["answer"],
                "reasoning": parsed_data["reasoning"],
            }
        else:
            return {
                "type": "simple",
                "content": f"✅ **Result:**\n\n```json\n{json_content}\n```",
                "answer": None,
                "reasoning": None,
            }


def _try_parse_agent_response(content: str) -> Dict[str, str]:
    """
    Try to parse agent response as JSON and extract answer/reasoning.

    Returns:
        Dict with 'answer' and 'reasoning' keys if successful, None otherwise.
    """
    try:
        # First try to parse as JSON directly
        if isinstance(content, str):
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # If direct parsing fails, try to find JSON-like structure in the string
                import re

                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    return None
        else:
            data = content

        # Check if it has the expected structure
        if isinstance(data, dict) and "answer" in data and "reasoning" in data:
            return {
                "answer": str(data["answer"]).strip(),
                "reasoning": str(data["reasoning"]).strip(),
            }

        return None
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return None


def process_message(message: str, graph_type: str, verbose: bool) -> Dict[str, Any]:
    """Process a user message and return the structured response."""
    if not message.strip():
        return {
            "type": "error",
            "content": "Please enter a message.",
            "answer": None,
            "reasoning": None,
        }

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

    # Create chat box and sidebar
    chat_box = create_default_chat_box(
        process_message_callback=process_message,
        get_example_queries_callback=get_example_queries,
    )
    sidebar = create_chat_sidebar()

    # Header
    st.title("🤖 FivcAdvisor")
    st.markdown(
        "*Intelligent Multi-Agent Task Processing with Advanced Graph Orchestration*"
    )
    st.markdown("---")

    # Render sidebar using sidebar component
    available_graphs = get_available_graphs()
    config = sidebar.render_for_chat_box(
        available_graphs=available_graphs,
        current_graph_type=st.session_state.graph_type,
        current_verbose=st.session_state.verbose,
        chat_box=chat_box,
        show_examples=True,
        max_examples=4,
    )

    # Update session state with sidebar configuration
    st.session_state.graph_type = config["graph_type"]
    st.session_state.verbose = config["verbose"]

    # Main chat interface using chat box
    chat_box.render_full_chat_interface(
        st.session_state.graph_type,
        st.session_state.verbose,
        title="💬 Chat with FivcAdvisor",
    )


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

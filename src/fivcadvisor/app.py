#!/usr/bin/env python
"""
FivcAdvisor Streamlit Web Application

A web interface for running FivcAdvisor graphs and interacting with the intelligent agent ecosystem.
"""

import time
from typing import Dict, Any
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv
from rich.console import Console

from fivcadvisor import (
    graphs,
    tools,
    # logs,
    settings,
)
from fivcadvisor.utils import (
    create_output_dir,
    # create_lazy_value,
)

# Load environment variables
load_dotenv()
settings.config()

# Configure Streamlit page
st.set_page_config(
    page_title="FivcAdvisor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize console for logging
console = Console()

# Initialize session state
if "graph_history" not in st.session_state:
    st.session_state.graph_history = []
if "current_graph" not in st.session_state:
    st.session_state.current_graph = None
if "graph_running" not in st.session_state:
    st.session_state.graph_running = False


def get_available_graphs() -> Dict[str, str]:
    """Get available graph types and their descriptions."""
    return {
        "general": "Intelligent task complexity assessment and execution",
        "simple": "Simple task execution with basic crew",
        "complex": "Complex task execution with advanced planning",
    }


def run_graph_sync(
    graph_type: str, query: str, verbose: bool = False
) -> Dict[str, Any]:
    """Run a graph synchronously and return results."""
    try:
        # Get graph creator
        graph = graphs.default_retriever.get(graph_type)
        if not graph:
            return {
                "success": False,
                "error": f"Unknown graph type: {graph_type}",
                "result": None,
            }

        # Create and run graph
        graph_run = graph(
            tools_retriever=tools.default_retriever,
            verbose=verbose,
            session_id=str(uuid4()),
        )

        with create_output_dir():
            # Execute the graph
            graph_result = graph_run.kickoff(inputs={"user_query": query})

            # Extract the actual result from the graph
            # The graph result might be the graph object itself, so we need to get the final result
            if hasattr(graph_run, "state") and hasattr(graph_run.state, "final_result"):
                actual_result = graph_run.state.final_result
            else:
                actual_result = graph_result

            # Process the result
            if actual_result is None:
                processed_result = {
                    "message": "Graph completed but no result was generated"
                }
            elif hasattr(actual_result, "to_dict"):
                processed_result = actual_result.to_dict()
            elif isinstance(actual_result, dict):
                processed_result = actual_result
            else:
                processed_result = {"raw_result": str(actual_result)}

            return {"success": True, "error": None, "result": processed_result}

    except Exception as e:
        return {"success": False, "error": str(e), "result": None}


def main():
    """Main Streamlit application."""

    # Header
    st.title("🤖 FivcAdvisor")
    st.markdown(
        "*Intelligent agent ecosystem for autonomous tool generation and dynamic crew orchestration*"
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Graph type selection
        graph_types = get_available_graphs()
        selected_graph = st.selectbox(
            "Select Graph Type",
            options=list(graph_types.keys()),
            format_func=lambda x: f"{x.title()} - {graph_types[x]}",
        )

        # Verbose mode
        verbose_mode = st.checkbox("Verbose Mode", value=False)

        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.graph_history = []
            st.rerun()

        st.divider()

        # Graph information
        st.header("ℹ️ Graph Information")
        st.markdown(f"**Selected Graph:** {selected_graph.title()}")
        st.markdown(f"**Description:** {graph_types[selected_graph]}")

        # Available graphs
        st.subheader("Available Graphs:")
        for graph, desc in graph_types.items():
            st.markdown(f"• **{graph.title()}**: {desc}")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("💬 Query Interface")

        # Query input
        query = st.text_area(
            "Enter your query:",
            height=100,
            placeholder="What would you like FivcAdvisor to help you with?",
            key="query_input",
        )

        # Run button
        run_button = st.button(
            "🚀 Run Graph",
            type="primary",
            disabled=st.session_state.graph_running or not query.strip(),
        )

        # Run graph when button is clicked
        if run_button and query.strip():
            st.session_state.graph_running = True

            with st.spinner(f"Running {selected_graph} graph..."):
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Simulate progress updates
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text("Initializing graph...")
                    elif i < 60:
                        status_text.text("Processing query...")
                    elif i < 90:
                        status_text.text("Executing tasks...")
                    else:
                        status_text.text("Finalizing results...")
                    time.sleep(0.02)  # Small delay for visual effect

                # Run the actual graph
                result = run_graph_sync(selected_graph, query, verbose_mode)

                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()

            # Store result in history
            graph_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "graph_type": selected_graph,
                "query": query,
                "result": result,
                "verbose": verbose_mode,
            }
            st.session_state.graph_history.insert(0, graph_entry)

            st.session_state.graph_running = False
            st.rerun()

        # Display current result
        if st.session_state.graph_history:
            latest_result = st.session_state.graph_history[0]

            st.header("📊 Latest Result")

            # Result metadata
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.metric("Graph Type", latest_result["graph_type"].title())
            with col_meta2:
                st.metric(
                    "Status",
                    "✅ Success" if latest_result["result"]["success"] else "❌ Error",
                )
            with col_meta3:
                st.metric("Timestamp", latest_result["timestamp"])

            # Result content
            if latest_result["result"]["success"]:
                st.success("Graph completed successfully!")

                # Display result
                if latest_result["result"]["result"]:
                    st.subheader("Result:")
                    if isinstance(latest_result["result"]["result"], dict):
                        st.json(latest_result["result"]["result"])
                    else:
                        st.text(latest_result["result"]["result"])
            else:
                st.error(f"Graph failed: {latest_result['result']['error']}")

    with col2:
        st.header("📈 Graph History")

        if st.session_state.graph_history:
            for i, entry in enumerate(
                st.session_state.graph_history[:10]
            ):  # Show last 10 entries
                with st.expander(
                    f"{entry['timestamp']} - {entry['graph_type'].title()}",
                    expanded=(i == 0),
                ):
                    st.markdown(
                        f"**Query:** {entry['query'][:100]}{'...' if len(entry['query']) > 100 else ''}"
                    )
                    st.markdown(f"**Graph:** {entry['graph_type']}")
                    st.markdown(f"**Verbose:** {'Yes' if entry['verbose'] else 'No'}")

                    if entry["result"]["success"]:
                        st.success("✅ Success")
                        if entry["result"]["result"]:
                            with st.expander("View Result"):
                                if isinstance(entry["result"]["result"], dict):
                                    st.json(entry["result"]["result"])
                                else:
                                    st.text(entry["result"]["result"])
                    else:
                        st.error(f"❌ Error: {entry['result']['error']}")
        else:
            st.info("No graph history yet. Run a graph to see results here.")

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>FivcAdvisor v0.1.0 - Intelligent Agent Ecosystem</p>
            <p>Built with Streamlit • Powered by CrewAI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple Graph Example

This example demonstrates how to use the SimpleGraph implementation
with LangGraph to process a user query.
"""

import asyncio
from uuid import uuid4

import dotenv
from fivcadvisor.graphs import create_simple_graph
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)
from fivcadvisor.utils import create_output_dir

dotenv.load_dotenv()


async def main():
    """Run the simple graph example."""
    print("FivcAdvisor - Simple Graph Example")
    print("=" * 50)

    # Create tools retriever and register tools
    tools_retriever = create_retriever()

    with create_output_dir():
        register_default_tools(tools_retriever=tools_retriever)
        register_mcp_tools(tools_retriever=tools_retriever)

        # Create simple graph
        graph = create_simple_graph()
        graph_run = graph(
            tools_retriever=tools_retriever,
            verbose=True,
            session_id=str(uuid4()),
        )

        # Test with a simple query
        user_query = "What is 2 + 2?"
        print(f"\nProcessing query: {user_query}")
        print("-" * 30)

        try:
            result = await graph_run.kickoff_async(inputs={"user_query": user_query})
            print(f"\nResult: {result}")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Complex Graph Example

This example demonstrates how to use the ComplexGraph implementation
with LangGraph to process complex queries that require planning and execution.
"""

import asyncio
from uuid import uuid4

import dotenv
from fivcadvisor.graphs import create_complex_graph
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)
from fivcadvisor.utils import create_output_dir

dotenv.load_dotenv()


async def main():
    """Run the complex graph example."""
    print("FivcAdvisor - Complex Graph Example")
    print("=" * 50)

    # Create tools retriever and register tools
    tools_retriever = create_retriever()
    
    with create_output_dir():
        register_default_tools(tools_retriever=tools_retriever)
        register_mcp_tools(tools_retriever=tools_retriever)
        
        # Create complex graph
        graph = create_complex_graph()
        graph_run = graph(
            tools_retriever=tools_retriever,
            verbose=True,
            session_id=str(uuid4()),
        )
        
        # Test with a complex query that requires planning
        user_query = (
            "Create a comprehensive analysis of renewable energy trends, "
            "including market research, technology assessment, and "
            "investment recommendations for the next 5 years."
        )
        
        print(f"\nProcessing complex query:")
        print(f"{user_query}")
        print("-" * 50)
        
        try:
            result = await graph_run.kickoff_async(inputs={"user_query": user_query})
            print(f"\nResult: {result}")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())

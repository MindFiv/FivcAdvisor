#!/usr/bin/env python3
"""
General Graph Example

This example demonstrates how to use the GeneralGraph implementation
with LangGraph to process user queries with automatic complexity routing.
"""

import asyncio
from uuid import uuid4

import dotenv
from fivcadvisor.graphs import create_general_graph
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)
from fivcadvisor.utils import create_output_dir

dotenv.load_dotenv()


async def main():
    """Run the general graph example."""
    print("FivcAdvisor - General Graph Example")
    print("=" * 50)

    # Create tools retriever and register tools
    tools_retriever = create_retriever()
    
    with create_output_dir():
        register_default_tools(tools_retriever=tools_retriever)
        register_mcp_tools(tools_retriever=tools_retriever)
        
        # Create general graph
        graph = create_general_graph()
        graph_run = create_general_graph(
            tools_retriever=tools_retriever,
            verbose=True,
            session_id=str(uuid4()),
        )
        
        # Test with different types of queries
        queries = [
            "What is 5 + 3?",  # Simple query
            "What is machine learning?",  # Potentially simple query
            "Research the latest trends in AI and create a comprehensive report",  # Complex query
        ]
        
        for i, user_query in enumerate(queries, 1):
            print(f"\n{i}. Processing query: {user_query}")
            print("-" * 50)
            
            try:
                result = await graph_run.kickoff_async(inputs={"user_query": user_query})
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

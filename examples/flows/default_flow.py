#!/usr/bin/env python
"""
Example script demonstrating the Default Flow

This example shows how the FivcAdvisor intelligently routes tasks
based on complexity assessment by a consultant agent.
"""
import asyncio
import sys
import os
from typing import Optional

# Add the src directory to the path so we can import fivcadvisor
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from fivcadvisor.tools import (
    create_retriever,
    create_default_tools,
    create_mcp_tools,
)
from fivcadvisor.flows import create_default_flow
from fivcadvisor.utils import create_output_dir
from fivcadvisor.tools.retrievers import ToolsRetriever


async def run_flow(
        user_query: Optional[str],
        tools_retriever: Optional[ToolsRetriever] = None,
):
    flow = create_default_flow(
        tools_retriever=tools_retriever, verbose=True)

    with create_output_dir().subdir('flows'):
        try:
            await flow.kickoff_async(inputs={'user_query': user_query})
            print("\nFlow completed successfully!")

        except KeyboardInterrupt:
            print("\nFlow interrupted by user.")

        except Exception as e:
            print(f"\nError running flow: {e}")
            print("Make sure you have:")
            print("1. Set up your API keys in .env file")
            print("2. Installed required dependencies")


async def main():
    """
    Run the default flow example
    """
    print("CrewAI Hatchery - Default Flow Example")
    print("=" * 50)

    print("This example demonstrates intelligent task assessment:")
    print("1. Consultant agent assesses task complexity")
    print("2. Simple tasks → Single work agent")
    print("3. Complex tasks → Director + specialized team")

    retriever = create_retriever()
    create_default_tools(tools_retriever=retriever)
    create_mcp_tools(tools_retriever=retriever)
    # Demonstrate both modes
    print("\n" + "=" * 50)
    user_query = "What are the key concepts in machine learning?"
    await run_flow(user_query, tools_retriever=retriever)


if __name__ == "__main__":
    asyncio.run(main())

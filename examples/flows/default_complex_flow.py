#!/usr/bin/env python
"""
Example script demonstrating the Default Flow

This example shows how the CrewAI Hatchery intelligently routes tasks
based on complexity assessment by a consultant agent.
"""
import asyncio
import sys
import os
from typing import Optional

from crewai_hatchery.tools import create_tools_retriever

# Add the src directory to the path so we can import crewai_hatchery
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai_hatchery.flows import create_default_complex_flow
from crewai_hatchery.utils import create_output_dir
from crewai_hatchery.tools.retrievers import ToolsRetriever


async def run_flow(
        user_query: str,
        tools_retriever: Optional[ToolsRetriever] = None,
):
    flow = create_default_complex_flow(
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
    print("CrewAI Hatchery - Default Complex Flow Example")
    print("=" * 50)

    print("This example demonstrates intelligent task planning:")
    print("1. Complex tasks → Planning crew")
    print("2. Planning crew outputs a plan")
    print("3. Plan is executed by a crew")

    retriever = create_tools_retriever()
    # Demonstrate both modes
    print("\n" + "=" * 50)
    result = await run_flow(
        'Plan a trip to Tokyo in the next five days',
        tools_retriever=retriever
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

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

# Add the src directory to the path so we can import crewai_hatchery
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai_hatchery.flows import create_default_flow
from crewai_hatchery.utils import create_output_dir


def run_flow(
        user_query: Optional[str],
        plot_file: str = '',
):
    flow = create_default_flow(user_query=user_query)
    output_dir = create_output_dir()

    with output_dir.subdir('flows'):
        try:
            flow.plot(plot_file)
            flow.kickoff()
            print("\nFlow completed successfully!")

        except KeyboardInterrupt:
            print("\nFlow interrupted by user.")

        except Exception as e:
            print(f"\nError running flow: {e}")
            print("Make sure you have:")
            print("1. Set up your API keys in .env file")
            print("2. Installed required dependencies")


def run_flow_predefined():
    print("\n--- Mode 1: Programmatic (with predefined query) ---")
    predefined_query = "What are the key concepts in machine learning?"
    print(f"\nRunning flow with predefined query: '{predefined_query}'")
    run_flow(predefined_query, 'predefined_flow')


def run_flow_interactive():
    print("\n--- Mode 2: Interactive (with user input) ---")
    # Run the interactive flow
    print("\nStarting interactive default flow...")
    run_flow(None, 'interactive_flow')


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

    # Demonstrate both modes
    print("\n" + "=" * 50)
    run_flow_predefined()

    print("\n" + "="*50)
    run_flow_interactive()


if __name__ == "__main__":
    asyncio.run(main())

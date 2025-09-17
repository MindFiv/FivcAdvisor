#!/usr/bin/env python
"""
Example script demonstrating the Default Flow

This example shows how the FivcAdvisor intelligently routes tasks
based on complexity assessment by a consultant agent.
"""
import asyncio
from typing import Optional

import dotenv
from fivcadvisor.tools import default_retriever
from fivcadvisor.tools.utils import retrievers
from fivcadvisor.logs import agent_logger
from fivcadvisor.flows import create_general_flow
from fivcadvisor.utils import create_output_dir


async def run_flow(
        user_query: Optional[str],
        tools_retriever: Optional[retrievers.ToolsRetriever] = None,
):
    flow = create_general_flow(
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
    print("FivcAdvisor - Default Flow Example")
    print("=" * 50)

    print("This example demonstrates intelligent task assessment:")
    print("1. Consultant agent assesses task complexity")
    print("2. Simple tasks → Single work agent")
    print("3. Complex tasks → Director + specialized team")

    dotenv.load_dotenv()
    agent_logger()
    default_retriever()

    # Demonstrate both modes
    print("\n" + "=" * 50)
    user_query = "What are the key concepts in machine learning?"
    await run_flow(
        user_query, tools_retriever=default_retriever())


if __name__ == "__main__":
    asyncio.run(main())

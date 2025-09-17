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
from fivcadvisor.logs import agent_logger
from fivcadvisor.flows import create_complex_flow
from fivcadvisor.utils import create_output_dir
from fivcadvisor.tools.utils.retrievers import ToolsRetriever


async def run_flow(
        user_query: str,
        tools_retriever: Optional[ToolsRetriever] = None,
):
    flow = create_complex_flow(
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
    print("FivcAdvisor - Default Complex Flow Example")
    print("=" * 50)

    print("This example demonstrates intelligent task planning:")
    print("1. Complex tasks → Planning crew")
    print("2. Planning crew outputs a plan")
    print("3. Plan is executed by a crew")

    dotenv.load_dotenv()
    agent_logger()
    default_retriever()
    # Demonstrate both modes
    print("\n" + "=" * 50)
    result = await run_flow(
        'Plan a trip to Tokyo in the next five days',
        tools_retriever=default_retriever()
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

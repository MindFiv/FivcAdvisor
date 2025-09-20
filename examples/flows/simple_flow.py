#!/usr/bin/env python
"""
Example script demonstrating the Default Flow

This example shows how the FivcAdvisor intelligently routes tasks
based on complexity assessment by a consultant agent.
"""
import asyncio
import dotenv

from fivcadvisor.listeners import register_default_events
from fivcadvisor.tools import (
    default_retriever,
    register_default_tools,
    register_mcp_tools,
)
from fivcadvisor.logs import agent_logger
from fivcadvisor.flows import create_simple_flow
from fivcadvisor.utils import create_output_dir


async def run_flow(
        user_query: str,
        tools_retriever=None,
):
    flow = create_simple_flow(
        tools_retriever=tools_retriever, verbose=False)

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
    print("FivcAdvisor - Default Simple Flow Example")
    print("=" * 50)

    print("This example demonstrates intelligent task assessment:")
    print("1. Consultant agent assesses task complexity")
    print("2. Simple tasks → Single work agent")
    print("3. Complex tasks → Incapable of handling")

    dotenv.load_dotenv()
    register_default_events(logger=agent_logger)
    register_default_tools(tools_retriever=default_retriever)
    register_mcp_tools(tools_retriever=default_retriever)

    print("\n" + "=" * 50)
    result = await run_flow(
        'What is the result of 3 power 10 and divide by 2?',
        tools_retriever=default_retriever
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

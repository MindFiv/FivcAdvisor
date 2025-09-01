import asyncio
import sys
import os

# Add the src directory to the path so we can import crewai_hatchery
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai_hatchery.utils import create_output_dir
from crewai_hatchery.tools import (
    create_retriever,
    create_default_tools,
    create_mcp_tools,
)


async def main():
    """
    Run the assessment crew example
    """

    print("CrewAI Hatchery - Tool Retriever Example")
    print("\n" + "=" * 50)

    retriever = create_retriever()

    # Create the retriever
    with create_output_dir():
        create_default_tools(tools_retriever=retriever)
        create_mcp_tools(tools_retriever=retriever)

        print("Waiting for retriever to complete...")
        print("\n" + "=" * 50)

        result = retriever.retrieve("How to become a millionaire? think step by step")
        print('\nResult:')
        for r in result:
            print('-------------------------')
            print(r)


if __name__ == '__main__':
    asyncio.run(main())

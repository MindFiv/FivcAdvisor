import asyncio
import sys
import os

# Add the src directory to the path so we can import fivcadvisor
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from fivcadvisor.utils import create_output_dir
from fivcadvisor.crews import create_assessing_crew
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)


async def main():
    """
    Run the assessment crew example
    """
    print("FivcAdvisor - Assessing Crew Example")
    print("=" * 50)

    tools_retriever = create_retriever()

    with create_output_dir():
        register_default_tools(tools_retriever=tools_retriever)
        register_mcp_tools(tools_retriever=tools_retriever)
        crew = create_assessing_crew(
            tools_retriever=tools_retriever, verbose=True)

    print("Waiting for crew to complete...")
    print("\n" + "=" * 50)
    result = crew.kickoff(inputs={
        'user_query': "What is machine learning?"
    })
    print(result)


if __name__ == '__main__':
    asyncio.run(main())

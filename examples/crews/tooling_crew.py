import asyncio
import sys
import os

# Add the src directory to the path so we can import fivcadvisor
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from fivcadvisor.crews import create_tooling_crew
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)
from fivcadvisor.utils import create_output_dir


async def main():
    """
    Run the assessment crew example
    """
    print("FivcAdvisor - Tooling Crew Example")
    print("\n" + "=" * 50)

    tools_retriever = create_retriever()

    with create_output_dir():
        register_default_tools(tools_retriever=tools_retriever)
        register_mcp_tools(tools_retriever=tools_retriever)
        crew = create_tooling_crew(
            tools_retriever=tools_retriever,
            verbose=True,
            output_log_file='tooling_crew.json',
        )

        print("Waiting for crew to complete...")
        print("=" * 50)
        result = await crew.kickoff_async(inputs={
            'user_query': "What time is it now?",
        })
        print(result)


if __name__ == '__main__':
    asyncio.run(main())

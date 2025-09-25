import asyncio
import dotenv

from fivcadvisor.utils import create_output_dir
from fivcadvisor.crews import create_assessing_crew
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)

dotenv.load_dotenv()


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
        crew = create_assessing_crew(tools_retriever=tools_retriever, verbose=True)
        crew_result = crew.kickoff(inputs={
            'user_query': "What is machine learning?"
        })
        print(str(crew_result))


if __name__ == '__main__':
    asyncio.run(main())

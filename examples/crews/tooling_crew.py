import asyncio
import dotenv

from fivcadvisor.crews import create_tooling_crew
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)
from fivcadvisor.utils import create_output_dir

dotenv.load_dotenv()


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
        crew_result = await crew.kickoff_async(inputs={
            'user_query': "What time is it now?",
        })
        print(crew_result.to_dict())


if __name__ == '__main__':
    asyncio.run(main())

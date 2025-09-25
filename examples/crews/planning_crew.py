import asyncio
import dotenv

from fivcadvisor.crews import create_planning_crew
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
    print("FivcAdvisor - Planning Crew Example")
    print("\n" + "=" * 50)

    tools_retriever = create_retriever()

    with create_output_dir():
        register_default_tools(tools_retriever=tools_retriever)
        register_mcp_tools(tools_retriever=tools_retriever)
        crew = create_planning_crew(
            tools_retriever=tools_retriever,
            verbose=True,
            output_log_file='planning_crew.json',
        )
        crew_result = await crew.kickoff_async(inputs={
            'user_query':
                "通过网上搜索，长期获取实时互联网上的内容，"
                "并从中提取一些有商业价值的信息，最终通过分析这些高商业价值的信息，"
                "形成一份商业报告。在其中可以告诉我们有哪些可以抓住的商机。",
        })
        print(str(crew_result))


if __name__ == '__main__':
    asyncio.run(main())

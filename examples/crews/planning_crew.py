import asyncio
import sys
import os

# Add the src directory to the path so we can import fivcadvisor
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from fivcadvisor.crews import create_planning_crew
from fivcadvisor.tools import (
    create_retriever,
    create_default_tools,
    create_mcp_tools,
)
from fivcadvisor.utils import create_output_dir


async def main():
    """
    Run the assessment crew example
    """
    print("FivcAdvisor - Planning Crew Example")
    print("\n" + "=" * 50)

    tools_retriever = create_retriever()

    with create_output_dir():
        create_default_tools(tools_retriever=tools_retriever)
        create_mcp_tools(tools_retriever=tools_retriever)
        crew = create_planning_crew(
            tools_retriever=tools_retriever,
            verbose=True,
            output_log_file='planning_crew.json',
        )

        print("Waiting for crew to complete...")
        print("\n" + "=" * 50)
        result = await crew.kickoff_async(inputs={
            'user_query':
                "通过网上搜索，长期获取实时互联网上的内容，"
                "并从中提取一些有商业价值的信息，最终通过分析这些高商业价值的信息，"
                "形成一份商业报告。在其中可以告诉我们有哪些可以抓住的商机。",
        })
        print(result)


if __name__ == '__main__':
    asyncio.run(main())

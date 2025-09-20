#!/usr/bin/env python
"""
Example script demonstrating the create_executing_crew function

This example shows how to create a crew from a predefined plan structure.
"""
import asyncio
import dotenv

from fivcadvisor.logs import create_agent_logger
from fivcadvisor.utils import create_output_dir
from fivcadvisor.tools import (
    create_retriever,
    register_default_tools,
    register_mcp_tools,
)
from fivcadvisor.crews import create_executing_crew
from fivcadvisor.models import CrewPlan

dotenv.load_dotenv()


async def main():
    """
    Run the planned crew example
    """
    print("FivcAdvisor - Planned Crew Example")
    print("\n" + "=" * 50)

    # Create a sample planning result structure
    sample_plan = CrewPlan(
        agents=[
            CrewPlan.Agent(
                role="Research Analyst",
                goal="Conduct thorough research on machine learning topics and provide comprehensive analysis",
                backstory="An experienced data scientist with expertise in machine learning research and analysis",
                tools=["Search the internet with Serper"],
            ),
            CrewPlan.Agent(
                role="Content Writer",
                goal="Create clear and engaging content based on research findings",
                backstory="A skilled technical writer with experience in making complex topics accessible",
                tools=[],
            )
        ],
        tasks=[
            CrewPlan.Task(
                description="Research the key concepts in machine learning and their applications",
                expected_output="A comprehensive list of machine learning concepts with detailed explanations",
                tools=[],
                requires_human=False,
            ),
            CrewPlan.Task(
                description="Write a clear and engaging summary of machine learning concepts for beginners",
                expected_output="A well-structured article explaining machine learning concepts in accessible language",
                tools=[],
                requires_human=True,
            )
        ]
    )

    print("Creating crew from plan...")
    print("\nPlan structure:")
    print(f"- Agents: {len(sample_plan.agents)}")
    for agent in sample_plan.agents:
        print(f"  * {agent.role}")
    print(f"- Tasks: {len(sample_plan.tasks)}")
    for task in sample_plan.tasks:
        print(f"  * {task.description[:50]}...")

    create_agent_logger()
    tools_retriever = create_retriever()

    with create_output_dir():
        register_default_tools(tools_retriever=tools_retriever)
        register_mcp_tools(tools_retriever=tools_retriever)
        crew = create_executing_crew(
            tools_retriever=tools_retriever,
            plan=sample_plan,
            verbose=True,
        )
        crew_result = crew.kickoff(inputs={
            "user_query":
                'Write an educative article on machine learning, '
                'aimed at beginners. And even primary students can understand.'
        })
        print(crew_result.to_dict())


if __name__ == '__main__':
    asyncio.run(main())

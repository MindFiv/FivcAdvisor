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
from fivcadvisor.models import TaskPlan

dotenv.load_dotenv()


async def main():
    """
    Run the planned crew example
    """
    print("FivcAdvisor - Planned Crew Example")
    print("\n" + "=" * 50)

    # Create a sample planning result structure
    sample_plan = TaskPlan(
        tasks=[
            TaskPlan.Task(
                agent_role="Research Analyst",
                agent_goal="Conduct thorough research on machine learning topics and provide comprehensive analysis",
                agent_backstory="An experienced data scientist with expertise in machine learning research and analysis",
                name="Research Machine Learning Concepts",
                description="Research the key concepts in machine learning and their applications",
                expected_output="A comprehensive list of machine learning concepts with detailed explanations",
                tools=[],
                requires_human=False,
            ),
            TaskPlan.Task(
                agent_role="Content Writer",
                agent_goal="Create clear and engaging content based on research findings",
                agent_backstory="A skilled technical writer with experience in making complex topics accessible",
                name="Write Summary Article",
                description="Write a clear and engaging summary of machine learning concepts for beginners",
                expected_output="A well-structured article explaining machine learning concepts in accessible language",
                tools=[],
                requires_human=True,
            )
        ]
    )

    print("Creating crew from plan...")
    print("\nPlan structure:")
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
        print(str(crew_result))


if __name__ == '__main__':
    asyncio.run(main())

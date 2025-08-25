#!/usr/bin/env python
"""
Example script demonstrating the create_executing_crew function

This example shows how to create a crew from a predefined plan structure.
"""
import asyncio
import sys
import os

from crewai_hatchery.tools import create_tools_retriever

# Add the src directory to the path so we can import crewai_hatchery
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai_hatchery.crews import create_executing_crew
from crewai_hatchery.outputs import PlanOutput


def main():
    """
    Run the planned crew example
    """
    print("CrewAI Hatchery - Planned Crew Example")
    print("\n" + "=" * 50)

    # Create a sample planning result structure
    tools_retriever = create_tools_retriever()
    sample_plan = PlanOutput(
        agents=[
            PlanOutput.Agent(
                role="Research Analyst",
                goal="Conduct thorough research on machine learning topics and provide comprehensive analysis",
                backstory="An experienced data scientist with expertise in machine learning research and analysis",
                tools=["Search the internet with Serper"],
            ),
            PlanOutput.Agent(
                role="Content Writer",
                goal="Create clear and engaging content based on research findings",
                backstory="A skilled technical writer with experience in making complex topics accessible",
                tools=[],
            )
        ],
        tasks=[
            PlanOutput.Task(
                description="Research the key concepts in machine learning and their applications",
                expected_output="A comprehensive list of machine learning concepts with detailed explanations",
            ),
            PlanOutput.Task(
                description="Write a clear and engaging summary of machine learning concepts for beginners",
                expected_output="A well-structured article explaining machine learning concepts in accessible language",
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

    try:
        crew = create_executing_crew(
            tools_retriever=tools_retriever,
            plan=sample_plan,
            verbose=True,
        )
        crew.kickoff(inputs={
            "user_query":
                'Write an educative article on machine learning, '
                'aimed at beginners. And even primary students can understand.'
        })

        print("\nCrew completed successfully!")

    except Exception as e:
        print(f"\n❌ Error creating crew: {e}")
        print("This might be due to missing dependencies or tool configuration issues.")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

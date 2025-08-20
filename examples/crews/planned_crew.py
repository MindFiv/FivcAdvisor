#!/usr/bin/env python
"""
Example script demonstrating the create_planned_crew function

This example shows how to create a crew from a predefined plan structure.
"""
import asyncio
import sys
import os

# Add the src directory to the path so we can import crewai_hatchery
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai_hatchery.crews import create_planned_crew
from crewai_hatchery.outputs import PlanningOutput


async def main():
    """
    Run the planned crew example
    """
    print("CrewAI Hatchery - Planned Crew Example")
    print("\n" + "=" * 50)

    # Create a sample planning result structure
    sample_plan = PlanningOutput(
        agents=[
            PlanningOutput.Agent(
                role="Research Analyst",
                goal="Conduct thorough research on machine learning topics and provide comprehensive analysis",
                backstory="An experienced data scientist with expertise in machine learning research and analysis",
                tools=[],
            ),
            PlanningOutput.Agent(
                role="Content Writer",
                goal="Create clear and engaging content based on research findings",
                backstory="A skilled technical writer with experience in making complex topics accessible",
                tools=[],
            )
        ],
        tasks=[
            PlanningOutput.Task(
                description="Research the key concepts in machine learning and their applications",
                expected_output="A comprehensive list of machine learning concepts with detailed explanations",
                tools=[],
            ),
            PlanningOutput.Task(
                description="Write a clear and engaging summary of machine learning concepts for beginners",
                expected_output="A well-structured article explaining machine learning concepts in accessible language",
                tools=[],
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
        crew = create_planned_crew(plan=sample_plan)
        print(f"\n✅ Successfully created crew with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
        
        print("\nCrew composition:")
        for i, agent in enumerate(crew.agents, 1):
            print(f"  Agent {i}: {agent.role}")
            print(f"    Goal: {agent.goal[:50]}...")
        
        for i, task in enumerate(crew.tasks, 1):
            print(f"  Task {i}: {task.description[:50]}...")
            print(f"    Agent: {task.agent.role}")
            print(f"    Tools: {len(task.tools) if task.tools else 0}")
        
        print("\n🎉 Crew creation successful! Ready to be executed with crew.kickoff()")

    except Exception as e:
        print(f"\n❌ Error creating crew: {e}")
        print("This might be due to missing dependencies or tool configuration issues.")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import sys
import os

# Add the src directory to the path so we can import crewai_hatchery
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai_hatchery.crews import create_assessing_crew
from crewai_hatchery.tools import create_tools_retriever


async def main():
    """
    Run the assessment crew example
    """
    print("CrewAI Hatchery - Assessing Crew Example")
    print("\n" + "=" * 50)

    crew = create_assessing_crew(
        tools_retriever=create_tools_retriever(), verbose=True)

    print("Waiting for crew to complete...")
    print("\n" + "=" * 50)
    result = crew.kickoff(inputs={
        'user_query': "What is machine learning?"
    })
    print(result)


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import sys
import os

# Add the src directory to the path so we can import crewai_hatchery
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), '..', 'src'))

from crewai_hatchery.utils import create_output_dir
from crewai_hatchery.embeddings import create_default_db
from crewai_hatchery.tools import create_tools_retriever


async def main():
    """
    Run the assessment crew example
    """

    print("CrewAI Hatchery - Tool Retriever Example")
    print("\n" + "=" * 50)

    # Create the retriever
    output_dir = create_output_dir()
    output_dir = output_dir.subdir("db")
    db = create_default_db(dir=str(output_dir))
    retriever = create_tools_retriever(db=db)

    print("Waiting for retriever to complete...")
    print("\n" + "=" * 50)

    result = retriever.retrieve("What time is it now?")
    print('\nResult:')
    for r in result:
        print(r)


if __name__ == '__main__':
    asyncio.run(main())

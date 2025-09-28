import asyncio
import dotenv

from fivcadvisor import agents

dotenv.load_dotenv()


async def main():
    """
    Run agent example
    """

    print("FivcAdvisor - Generic Agent Example")
    print("\n" + "=" * 50)

    agent = agents.create_default_agent()
    result = agent("Hi, how are you?")
    print(result)

    print(f'Result: {str(result)}')


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import dotenv

from fivcadvisor.utils import create_output_dir
from fivcadvisor.tools import (
    ToolsRetriever,
    ToolsLoader,
    register_default_tools,
)

dotenv.load_dotenv()


async def main():
    """
    Run the tool retriever example.
    """

    print("FivcAdvisor - Tool Retriever Example")
    print("\n" + "=" * 50)

    retriever = ToolsRetriever()

    # Create the retriever
    with create_output_dir():
        register_default_tools(tools_retriever=retriever)

        # Load MCP tools using ToolsLoader
        loader = ToolsLoader(retriever=retriever)
        await loader.load_async()

        print("Waiting for retriever to complete...")
        print("\n" + "=" * 50)

        result = retriever.retrieve("How to become a millionaire? think step by step")
        print('\nResult:')
        for r in result:
            print('-------------------------')
            print(r)


if __name__ == '__main__':
    asyncio.run(main())

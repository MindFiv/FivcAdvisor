"""
Tool Retriever Example

This example demonstrates how to use the ToolsRetriever to:
1. Load MCP tools from configured servers
2. Retrieve tools based on semantic search
3. Use retrieved tools with agents
"""

import asyncio
import dotenv

from fivcadvisor.utils import OutputDir
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

    # Create a retriever instance
    retriever = ToolsRetriever()

    # Use OutputDir context manager for proper directory handling
    with OutputDir():
        # Register default tools (currently empty, tools come from MCP servers)
        register_default_tools(tools_retriever=retriever)

        # Load MCP tools using ToolsLoader
        print("Loading MCP tools...")
        loader = ToolsLoader(tools_retriever=retriever)
        await loader.load_async()

        print("Tools loaded successfully!")
        print("\n" + "=" * 50)

        # Retrieve tools based on semantic search
        query = "How to become a millionaire? think step by step"
        print(f"\nQuery: {query}")
        print("\nRetrieving relevant tools...")

        result = retriever.retrieve(query)

        print(f'\nFound {len(result)} relevant tools:')
        for i, tool in enumerate(result, 1):
            print('-------------------------')
            print(f"Tool {i}: {tool}")


if __name__ == '__main__':
    asyncio.run(main())

"""
Agent Example - MCP Tools Integration

This example demonstrates how to use FivcAdvisor agents with MCP (Model Context Protocol) tools.
It shows:
1. Loading MCP tools (chrome-devtools) from configured servers
2. Creating an agent with MCP tools
3. Invoking the agent with a query that requires tool usage
4. Handling agent responses with tool calls

The example uses chrome-devtools MCP server to perform web searches and browsing tasks.

Prerequisites:
    - MCP servers configured in configs/mcp.yaml (chrome-devtools, sequential-thinking)
    - OpenAI API key set in environment (for LLM)
    - Node.js and npm installed (for MCP servers)

Usage:
    python examples/agents/run_agent_mcp.py

Expected Output:
    - Loads 28 tools from configured MCP servers
    - Creates a companion agent with these tools
    - Invokes the agent with a Chinese query: "在百度上查询携程股价" (Search for Ctrip stock price on Baidu)
    - Agent attempts to use chrome-devtools to navigate and search
"""

import asyncio
import dotenv
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from fivcadvisor.tools.types.configs import ToolsConfig
from fivcadvisor import agents
from fivcadvisor.agents.types import AgentsMonitor

dotenv.load_dotenv()


async def main():
    """
    Run agent example demonstrating MCP tools integration.
    """

    print("FivcAdvisor - Agent with MCP Tools Example")
    print("\n" + "=" * 70)

    # Step 1: Load MCP configuration and tools
    print("Step 1: Loading MCP tools from configured servers...")
    print("-" * 70)

    try:
        # Load MCP configuration from configs/mcp.yaml
        # This file contains the configuration for MCP servers like chrome-devtools
        config = ToolsConfig(config_file="configs/mcp.yaml", load=True)
        errors = config.get_errors()
        if errors:
            print(f"⚠ Config errors: {errors}")
            return

        # Create MCP client with configured servers
        # Each server is configured with a command and arguments to start the MCP server
        connections = {
            server_name: config.get(server_name).connection
            for server_name in config.list()
        }

        print(f"Configured servers: {list(connections.keys())}")

        # Create MultiServerMCPClient to manage connections to all MCP servers
        # This client handles the communication with each MCP server
        client = MultiServerMCPClient(connections)

        # Load tools from all configured servers
        # Each MCP server exposes a set of tools that can be used by the agent
        all_tools = []
        for server_name in client.connections.keys():
            try:
                # Get all tools from this MCP server
                tools = await client.get_tools(server_name=server_name)
                all_tools.extend(tools)
                print(f"✓ Loaded {len(tools)} tools from {server_name}")
            except Exception as e:
                print(f"⚠ Error loading tools from {server_name}: {e}")

        print(f"\n✓ Successfully loaded {len(all_tools)} tools total")
        print("\nAvailable tools:")
        for tool in all_tools:
            desc = tool.description[:60] if tool.description else "No description"
            print(f"  - {tool.name}: {desc}...")
        print()

        # Step 2: Create a companion agent with loaded MCP tools
        print("Step 2: Creating companion agent with MCP tools...")
        print("-" * 70)

        # Create an AgentsMonitor to track agent execution
        agent_monitor = AgentsMonitor()

        # Create a companion agent with all loaded MCP tools
        # The agent will use these tools to fulfill user requests
        agent = agents.create_companion_agent(
            callback_handler=agent_monitor,
            tools=all_tools  # Pass all loaded MCP tools to the agent
        )
        print(f"✓ Agent created successfully")
        print(f"  Agent ID: {agent.id}")
        print(f"  Agent Name: {agent.name}")
        print()

        # Step 3: Invoke agent with a query requiring tool usage
        print("Step 3: Invoking agent with a query requiring tool usage...")
        print("-" * 70)

        # Query in Chinese: "Search for Ctrip stock price on Baidu"
        # This query requires the agent to:
        # 1. Create a new browser page using chrome-devtools
        # 2. Navigate to Baidu (https://www.baidu.com)
        # 3. Search for "携程股价" (Ctrip stock price)
        # 4. Extract and return the results
        query = "在百度上查询携程股价"
        print(f"Query: {query}")
        print()

        print("Agent is processing your request...")
        print("-" * 70)

        try:
            # Run the agent asynchronously
            # The agent will use the MCP tools to complete the task
            result = await agent.run_async(query=query)

            print("\n✓ Agent response received:")
            print("-" * 70)
            print(result)
            print()

        except Exception as e:
            print(f"\n✗ Error during agent execution: {e}")
            print("\nNote: This is expected if the browser tools haven't been properly initialized.")
            print("The agent attempted to use the chrome-devtools MCP tools to complete the task.")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 70)
        print("Example completed!")
        print("\nKey Takeaways:")
        print("1. MCP tools were successfully loaded from configured servers")
        print("2. Agent was created with access to these tools")
        print("3. Agent attempted to use the tools to fulfill the user's request")
        print("4. Tool execution can be monitored and debugged using AgentsMonitor")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())

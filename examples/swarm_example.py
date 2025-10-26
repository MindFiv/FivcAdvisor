"""
LangGraph Swarm Example

This example demonstrates how to use the LangGraph Swarm adapter to create
a multi-agent system with specialized agents that can hand off tasks to each other.

The swarm uses LangChain agents with LangGraph for orchestration, providing
a powerful multi-agent architecture.
"""

import asyncio
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from fivcadvisor.agents import create_default_agent, create_swarm


# Define some example tools
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"


@tool
def analyze_data(data: str) -> str:
    """Analyze data and provide insights."""
    return f"Analysis of: {data}"


@tool
def write_report(content: str) -> str:
    """Write a report based on content."""
    return f"Report generated from: {content}"


async def main():
    """Main example function."""
    
    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Create specialized agents
    researcher = create_default_agent(
        model=llm,
        tools=[search_web],
        system_prompt=(
            "You are a research specialist. Your job is to search for information "
            "and gather data. When you have enough information, hand off to the analyst."
        ),
        name="Researcher",
    )
    
    analyst = create_default_agent(
        model=llm,
        tools=[analyze_data],
        system_prompt=(
            "You are a data analyst. Your job is to analyze information and provide insights. "
            "When analysis is complete, hand off to the writer."
        ),
        name="Analyst",
    )
    
    writer = create_default_agent(
        model=llm,
        tools=[write_report],
        system_prompt=(
            "You are a technical writer. Your job is to write clear, comprehensive reports. "
            "You are the final step in the process."
        ),
        name="Writer",
    )
    
    # Create the swarm
    swarm = create_swarm(
        agents=[researcher, analyst, writer],
        default_agent_name="Researcher",
    )
    
    # Example 1: Simple query
    print("=" * 60)
    print("Example 1: Simple Query")
    print("=" * 60)
    
    query = "Research and analyze the latest trends in AI"
    print(f"Query: {query}\n")
    
    try:
        result = await swarm.invoke_async(query)
        print(f"Result: {result}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 2: Using synchronous invoke
    print("=" * 60)
    print("Example 2: Synchronous Invocation")
    print("=" * 60)
    
    query = "What are the key metrics for evaluating AI systems?"
    print(f"Query: {query}\n")
    
    try:
        result = swarm.invoke(query)
        print(f"Result: {result}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 3: Access swarm properties
    print("=" * 60)
    print("Example 3: Swarm Properties")
    print("=" * 60)
    
    print(f"Number of agents: {len(swarm.agents)}")
    print(f"Agent names: {[agent.name for agent in swarm.agents]}")
    print(f"Default agent: {swarm.default_agent_name}")
    print()


if __name__ == "__main__":
    asyncio.run(main())


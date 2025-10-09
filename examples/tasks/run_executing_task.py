#!/usr/bin/env python3
"""
Example: Run execution task using Strands agents swarm

This example demonstrates how to use the run_executing_task function
to execute a complex query using a team of specialized agents.
"""

import asyncio
import dotenv

from fivcadvisor import tasks, tools

dotenv.load_dotenv()


async def main():
    """
    Run execution task example
    """
    print("FivcAdvisor - Execution Task Example")
    print("=" * 60)
    
    # Example query that requires multiple specialized agents
    query = "Research the latest trends in AI and create a comprehensive report"
    
    print(f"\n📝 Query: {query}")
    print("=" * 60)
    
    # Step 1: Assess the task
    print("\n🔍 Step 1: Assessing the task...")
    assessment = await tasks.run_assessing_task(query)
    print(f"   Require Planning: {assessment.require_planning}")
    print(f"   Required Tools: {assessment.require_tools}")
    print(f"   Reasoning: {assessment.reasoning}")
    
    # Step 2: Create a plan if needed
    if assessment.require_planning:
        print("\n📋 Step 2: Creating execution plan...")
        plan = await tasks.run_planning_task(query)
        print(f"   Team Size: {len(plan.specialists)} specialists")
        
        for i, specialist in enumerate(plan.specialists, 1):
            print(f"\n   Specialist {i}: {specialist.name}")
            print(f"      Backstory: {specialist.backstory[:100]}...")
            print(f"      Tools: {', '.join(specialist.tools)}")
        
        # Step 3: Execute the task using the swarm
        print("\n🚀 Step 3: Executing task with agent swarm...")
        result = await tasks.run_executing_task(
            query=query,
            plan=plan,
            tools_retriever=tools.default_retriever
        )
        
        print("\n✅ Execution Result:")
        print("=" * 60)
        print(result)
        print("=" * 60)
    else:
        print("\n✅ Task is simple and doesn't require planning")
        print("   You can handle this with a single agent")


if __name__ == '__main__':
    asyncio.run(main())


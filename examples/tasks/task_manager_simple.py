#!/usr/bin/env python3
"""
Simple example demonstrating TaskManager usage.

This example shows how to:
1. Create a TaskManager with persistence
2. Create and execute tasks
3. Query task status and events
4. Save and load task history
"""

import asyncio
import dotenv

from fivcadvisor import schemas, tools
from fivcadvisor.tasks.types import TaskManager
from fivcadvisor.utils import OutputDir

dotenv.load_dotenv()


async def main():
    print("=" * 60)
    print("TaskManager Simple Example")
    print("=" * 60)

    # 1. Create TaskManager with persistence
    print("\n1️⃣ Creating TaskManager with persistence...")
    manager = TaskManager(
        auto_save=True,  # Automatically save after changes
    )
    output_dir = manager.output_dir
    print(f"✅ TaskManager created")
    print(f"   Output directory: {output_dir}")
    print(f"   Auto-save: Enabled")
    print(f"   Each task will be saved as: task_{{tracer_id}}.json")

    # 2. Define a simple task plan
    print("\n2️⃣ Creating task plan...")
    plan = schemas.TaskTeam(
        specialists=[
            schemas.TaskTeam.Specialist(
                name="Calculator",
                backstory="Expert at mathematical calculations",
                tools=["calculator"],
            ),
        ]
    )
    print("✅ Task plan created with 1 specialist")

    # 3. Create task with event callback
    print("\n3️⃣ Creating task with event tracking...")

    def on_event(event):
        """Callback function to track task events"""
        print(f"   📋 Event: {event.agent_name} - {event.status.value}")
        if event.error:
            print(f"      ❌ Error: {event.error}")
        elif event.result:
            print(f"      ✅ Result: {event.result}")

    swarm = manager.create_task(
        plan=plan,
        tools_retriever=tools.default_retriever,
        on_event=on_event,
    )
    print("✅ Task created")

    # 4. Execute the task
    print("\n4️⃣ Executing task...")
    query = "Calculate 123 * 456"
    print(f"   Query: {query}")

    try:
        result = await swarm.invoke_async(query)
        print(f"\n✅ Task completed!")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"\n❌ Task failed: {e}")

    # 5. Query task information
    print("\n5️⃣ Querying task information...")
    print(f"   Total tasks: {len(manager.list_tasks())}")

    for tracer in manager.list_tasks():
        print(f"\n   Task ID: {tracer.id}")
        events = tracer.list_events()
        print(f"   Total events: {len(events)}")

        for event in events:
            print(f"\n   📊 Event Details:")
            print(f"      Agent: {event.agent_name}")
            print(f"      Status: {event.status.value}")
            print(f"      Query: {event.query}")
            if event.duration:
                print(f"      Duration: {event.duration:.2f}s")
            if event.result:
                print(f"      Result: {event.result}")

    # 6. Custom statistics
    print("\n6️⃣ Custom statistics...")
    total_events = 0
    status_counts = {}

    for tracer in manager.list_tasks():
        for event in tracer.list_events():
            total_events += 1
            status = event.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

    print(f"   Total events: {total_events}")
    print(f"   By status:")
    for status, count in status_counts.items():
        print(f"      {status}: {count}")

    # 7. Save task history
    print("\n7️⃣ Saving task history...")
    manager.save()
    print(f"✅ Task history saved")
    print(f"   Each task saved as: ./data/task_{{tracer_id}}.json")

    # List saved files
    import os
    task_files = [f for f in os.listdir(str(output_dir)) if f.startswith("task_")]
    print(f"   Found {len(task_files)} task files:")
    for f in task_files:
        print(f"      - {f}")

    # 8. Demonstrate loading
    print("\n8️⃣ Demonstrating load from directory...")
    new_manager = TaskManager(output_dir=output_dir)
    print(f"✅ Automatically loaded {len(new_manager.list_tasks())} tasks")
    print(f"   Tasks are loaded from all task_*.json files in output_dir")

    print("\n" + "=" * 60)
    print("Example completed successfully! 🎉")
    print("=" * 60)
    print("\n💡 Tip: Each task is saved in its own file for easy management")
    print("💡 Tip: TaskManager automatically loads all tasks on initialization")


if __name__ == "__main__":
    asyncio.run(main())

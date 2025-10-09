#!/usr/bin/env python3
"""
Advanced example demonstrating TaskManager with multiple tasks.

This example shows:
1. Managing multiple concurrent tasks
2. Custom event tracking and filtering
3. Task cleanup and management
4. Advanced statistics and reporting
"""

import asyncio
import dotenv

from datetime import datetime
from collections import defaultdict
from fivcadvisor import schemas, tools
from fivcadvisor.tasks.types import TaskManager, TaskStatus
from fivcadvisor.utils import OutputDir

dotenv.load_dotenv()


class TaskMonitor:
    """Custom task monitor with advanced tracking"""

    def __init__(self):
        self.events = []
        self.start_time = datetime.now()

    def on_event(self, event):
        """Track all events"""
        self.events.append({
            "timestamp": datetime.now(),
            "agent": event.agent_name,
            "status": event.status.value,
            "query": event.query,
        })
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] "
              f"{event.agent_name}: {event.status.value}")

    def get_summary(self):
        """Generate custom summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "total_events": len(self.events),
            "duration": duration,
            "events_per_second": len(self.events) / duration if duration > 0 else 0,
        }


async def create_and_run_task(manager, task_name, query, monitor):
    """Helper function to create and run a task"""
    print(f"\n🚀 Starting task: {task_name}")
    print(f"   Query: {query}")

    # Create task plan
    plan = schemas.TaskTeam(
        specialists=[
            schemas.TaskTeam.Specialist(
                name=task_name,
                backstory=f"Expert at {task_name.lower()}",
                tools=["calculator"],
            ),
        ]
    )

    # Create and execute task
    task = manager.create_task(
        plan=plan,
        tools_retriever=tools.default_retriever,
        on_event=monitor.on_event,
    )

    try:
        result = await task.invoke_async(query)
        print(f"✅ {task_name} completed: {result}")
        return result
    except Exception as e:
        print(f"❌ {task_name} failed: {e}")
        return None


async def main():
    print("=" * 70)
    print("TaskManager Advanced Example - Multiple Tasks")
    print("=" * 70)

    # Initialize
    manager = TaskManager(
        auto_save=True,
    )
    output_dir = manager.output_dir
    print(f"Output directory: {output_dir}")
    print(f"Auto-save: Enabled (each task saved as task_{{tracer_id}}.json)")
    monitor = TaskMonitor()

    # Define multiple tasks
    tasks = [
        ("Calculator-1", "Calculate 123 * 456"),
        ("Calculator-2", "Calculate 789 + 321"),
        ("Calculator-3", "Calculate 1000 / 25"),
    ]

    # Execute tasks sequentially
    print("\n📋 Executing multiple tasks...")
    results = []
    for task_name, query in tasks:
        result = await create_and_run_task(manager, task_name, query, monitor)
        results.append((task_name, result))
        await asyncio.sleep(0.5)  # Small delay between tasks

    # Display results
    print("\n" + "=" * 70)
    print("📊 Task Results Summary")
    print("=" * 70)
    for task_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {task_name}: {result}")

    # Analyze all tasks
    print("\n" + "=" * 70)
    print("📈 Detailed Task Analysis")
    print("=" * 70)

    print(f"\n1️⃣ Total Tasks: {len(manager.list_tasks())}")

    # Analyze each task
    for i, tracer in enumerate(manager.list_tasks(), 1):
        print(f"\n   Task {i}: {tracer.id}")
        events = tracer.list_events()
        print(f"   Events: {len(events)}")

        for event in events:
            if event.status == TaskStatus.COMPLETED:
                print(f"      ✅ Completed in {event.duration:.2f}s")
            elif event.status == TaskStatus.FAILED:
                print(f"      ❌ Failed: {event.error}")
            elif event.status == TaskStatus.RUNNING:
                print(f"      🔄 Running...")

    # Custom statistics
    print("\n2️⃣ Custom Statistics:")
    
    # Count by status
    status_counts = defaultdict(int)
    total_duration = 0
    completed_count = 0

    for tracer in manager.list_tasks():
        for event in tracer.list_events():
            status_counts[event.status.value] += 1
            if event.status == TaskStatus.COMPLETED and event.duration:
                total_duration += event.duration
                completed_count += 1

    print(f"\n   Status Distribution:")
    for status, count in status_counts.items():
        print(f"      {status}: {count}")

    if completed_count > 0:
        avg_duration = total_duration / completed_count
        print(f"\n   Performance:")
        print(f"      Average duration: {avg_duration:.2f}s")
        print(f"      Total duration: {total_duration:.2f}s")

    # Monitor summary
    print("\n3️⃣ Monitor Summary:")
    summary = monitor.get_summary()
    print(f"   Total events tracked: {summary['total_events']}")
    print(f"   Total time: {summary['duration']:.2f}s")
    print(f"   Events/second: {summary['events_per_second']:.2f}")

    # Filter events by status
    print("\n4️⃣ Event Filtering:")
    
    completed_events = []
    failed_events = []
    
    for tracer in manager.list_tasks():
        for event in tracer.list_events():
            if event.status == TaskStatus.COMPLETED:
                completed_events.append(event)
            elif event.status == TaskStatus.FAILED:
                failed_events.append(event)

    print(f"   Completed events: {len(completed_events)}")
    print(f"   Failed events: {len(failed_events)}")

    # Task cleanup demonstration
    print("\n5️⃣ Task Management:")
    print(f"   Current tasks: {len(manager.list_tasks())}")
    
    # Get first task ID
    if manager.list_tasks():
        first_task_id = manager.list_tasks()[0].id
        print(f"   Deleting task: {first_task_id}")
        manager.delete_task(first_task_id)
        print(f"   Remaining tasks: {len(manager.list_tasks())}")

    # Save final state
    print("\n6️⃣ Saving task history...")
    manager.save()
    print(f"   ✅ Saved all tasks")

    # List saved files
    import os
    task_files = [f for f in os.listdir(str(output_dir)) if f.startswith("task_")]
    print(f"   Found {len(task_files)} task files:")
    for f in task_files[:3]:  # Show first 3
        print(f"      - {f}")
    if len(task_files) > 3:
        print(f"      ... and {len(task_files) - 3} more")

    # Demonstrate loading and querying
    print("\n7️⃣ Loading and querying saved data...")
    loaded_manager = TaskManager(output_dir=output_dir)

    print(f"   Automatically loaded {len(loaded_manager.list_tasks())} tasks")

    # Query specific task
    if loaded_manager.list_tasks():
        task_id = loaded_manager.list_tasks()[0].id
        task = loaded_manager.get_task(task_id)
        if task:
            print(f"   Retrieved task: {task_id}")
            print(f"   Events in task: {len(task.list_events())}")

    print("\n" + "=" * 70)
    print("Advanced example completed successfully! 🎉")
    print("=" * 70)

    # Cleanup option
    print("\n💡 Tip: Use manager.cleanup() to clear all tasks and files")
    print("💡 Tip: Each task is saved in its own file for easy management")
    print(f"💡 Tip: Check {output_dir} directory for all task files")


if __name__ == "__main__":
    asyncio.run(main())


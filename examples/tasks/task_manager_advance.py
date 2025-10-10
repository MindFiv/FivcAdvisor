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
from fivcadvisor.tasks.types.repositories.files import FileTaskRuntimeRepository
from fivcadvisor.utils import OutputDir

dotenv.load_dotenv()


class StepTracker:
    """Custom step tracker with advanced tracking"""

    def __init__(self):
        self.steps = []
        self.start_time = datetime.now()

    def on_step_update(self, step):
        """Track all execution steps"""
        self.steps.append({
            "timestamp": datetime.now(),
            "agent": step.agent_name,
            "status": step.status.value,
        })
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] "
              f"{step.agent_name}: {step.status.value}")

    def get_summary(self):
        """Generate custom summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "total_steps": len(self.steps),
            "duration": duration,
            "steps_per_second": len(self.steps) / duration if duration > 0 else 0,
        }


async def create_and_run_task(manager, task_name, query, step_tracker):
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
    swarm = manager.create_task(
        plan=plan,
        tools_retriever=tools.default_retriever,
        on_event=step_tracker.on_step_update,
    )

    try:
        result = await swarm.invoke_async(query)
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
    output_dir = OutputDir().subdir('tasks')
    repo = FileTaskRuntimeRepository(output_dir=output_dir)
    manager = TaskManager(runtime_repo=repo)

    print(f"Output directory: {output_dir}")
    print(f"Repository: FileTaskRuntimeRepository")
    print(f"Tasks will be saved in: {output_dir}/task_<task_id>/")

    step_tracker = StepTracker()

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
        result = await create_and_run_task(manager, task_name, query, step_tracker)
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

    task_runtimes = manager.list_tasks()
    print(f"\n1️⃣ Total Tasks: {len(task_runtimes)}")

    # Analyze each task
    for i, task_runtime in enumerate(task_runtimes, 1):
        print(f"\n   Task {i}: {task_runtime.id}")

        # Get task monitor to access steps
        task_monitor = manager.get_task(task_runtime.id)
        if task_monitor:
            steps = task_monitor.list_steps()
            print(f"   Steps: {len(steps)}")

            for step in steps:
                if step.status == TaskStatus.COMPLETED:
                    if step.duration:
                        print(f"      ✅ Completed in {step.duration:.2f}s")
                    else:
                        print(f"      ✅ Completed")
                elif step.status == TaskStatus.FAILED:
                    print(f"      ❌ Failed: {step.error}")
                elif step.status == TaskStatus.EXECUTING:
                    print(f"      🔄 Running...")

    # Custom statistics
    print("\n2️⃣ Custom Statistics:")

    # Count by status
    status_counts = defaultdict(int)
    total_duration = 0
    completed_count = 0

    for task_runtime in manager.list_tasks():
        task_monitor = manager.get_task(task_runtime.id)
        if task_monitor:
            for step in task_monitor.list_steps():
                status_counts[step.status.value] += 1
                if step.status == TaskStatus.COMPLETED and step.duration:
                    total_duration += step.duration
                    completed_count += 1

    print(f"\n   Status Distribution:")
    for status, count in status_counts.items():
        print(f"      {status}: {count}")

    if completed_count > 0:
        avg_duration = total_duration / completed_count
        print(f"\n   Performance:")
        print(f"      Average duration: {avg_duration:.2f}s")
        print(f"      Total duration: {total_duration:.2f}s")

    # Step tracker summary
    print("\n3️⃣ Step Tracker Summary:")
    summary = step_tracker.get_summary()
    print(f"   Total steps tracked: {summary['total_steps']}")
    print(f"   Total time: {summary['duration']:.2f}s")
    print(f"   Steps/second: {summary['steps_per_second']:.2f}")

    # Filter steps by status
    print("\n4️⃣ Step Filtering:")

    completed_steps = []
    failed_steps = []

    for task_runtime in manager.list_tasks():
        task_monitor = manager.get_task(task_runtime.id)
        if task_monitor:
            for step in task_monitor.list_steps():
                if step.status == TaskStatus.COMPLETED:
                    completed_steps.append(step)
                elif step.status == TaskStatus.FAILED:
                    failed_steps.append(step)

    print(f"   Completed steps: {len(completed_steps)}")
    print(f"   Failed steps: {len(failed_steps)}")

    # Task cleanup demonstration
    print("\n5️⃣ Task Management:")
    task_list = manager.list_tasks()
    print(f"   Current tasks: {len(task_list)}")

    # Get first task ID
    if task_list:
        first_task_id = task_list[0].id
        print(f"   Deleting task: {first_task_id}")
        manager.delete_task(first_task_id)
        print(f"   Remaining tasks: {len(manager.list_tasks())}")

    # Task persistence
    print("\n6️⃣ Task persistence...")
    print(f"   ✅ Tasks are automatically persisted to disk")

    # List saved task directories
    import os
    task_dirs = [d for d in os.listdir(str(output_dir)) if d.startswith("task_")]
    print(f"   Found {len(task_dirs)} task directories:")
    for d in task_dirs[:3]:  # Show first 3
        print(f"      - {d}")
    if len(task_dirs) > 3:
        print(f"      ... and {len(task_dirs) - 3} more")

    # Demonstrate loading and querying
    print("\n7️⃣ Loading and querying saved data...")
    loaded_repo = FileTaskRuntimeRepository(output_dir=output_dir)
    loaded_manager = TaskManager(runtime_repo=loaded_repo)

    loaded_tasks = loaded_manager.list_tasks()
    print(f"   Automatically loaded {len(loaded_tasks)} tasks")

    # Query specific task
    if loaded_tasks:
        task_id = loaded_tasks[0].id
        task = loaded_manager.get_task(task_id)
        if task:
            print(f"   Retrieved task: {task_id}")
            print(f"   Steps in task: {len(task.list_steps())}")

    print("\n" + "=" * 70)
    print("Advanced example completed successfully! 🎉")
    print("=" * 70)

    # Cleanup option
    print("\n💡 Tip: Use manager.delete_task(task_id) to delete specific tasks")
    print("💡 Tip: Each task is saved in its own directory with task.json and steps/")
    print(f"💡 Tip: Check {output_dir} directory for all task directories")
    print("💡 Tip: TaskManager uses FileTaskRuntimeRepository for persistence")


if __name__ == "__main__":
    asyncio.run(main())


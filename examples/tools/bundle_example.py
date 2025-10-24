#!/usr/bin/env python3
"""
Example demonstrating the Tool Bundle system.

This example shows how to:
1. Create and manage tool bundles
2. Retrieve tools with bundle expansion
3. Use bundle filters for selective expansion
"""

import sys
sys.path.insert(0, "src")

from unittest.mock import Mock
from fivcadvisor.tools.types import ToolsRetriever, ToolsBundle, ToolsBundleManager


def create_mock_tool(name: str, description: str) -> Mock:
    """Create a mock tool for demonstration."""
    tool = Mock()
    tool.tool_name = name
    tool.tool_spec = {"description": description}
    return tool


def example_basic_bundle_usage():
    """Example 1: Basic bundle creation and usage."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Bundle Creation and Usage")
    print("=" * 60)

    # Create a bundle manager
    manager = ToolsBundleManager()

    # Create a bundle for browser automation tools
    browser_bundle = manager.create_bundle(
        "browser_automation", metadata={"client": "playwright"}
    )

    # Create some mock tools
    click_tool = create_mock_tool("playwright_click", "Click on an element")
    navigate_tool = create_mock_tool("playwright_navigate", "Navigate to a URL")
    screenshot_tool = create_mock_tool("playwright_screenshot", "Take a screenshot")

    # Add tools to the bundle using the manager
    manager.add_tool_to_bundle("browser_automation", click_tool)
    manager.add_tool_to_bundle("browser_automation", navigate_tool)
    manager.add_tool_to_bundle("browser_automation", screenshot_tool)

    # Get bundle information
    info = manager.get_bundle_info("browser_automation")
    print(f"\nBundle Info: {info}")

    # Get all tools in the bundle
    tools = manager.get_bundle_tools("browser_automation")
    print(f"\nTools in bundle: {[t.tool_name for t in tools]}")


def example_tool_expansion():
    """Example 2: Tool expansion with bundles."""
    print("\n" + "=" * 60)
    print("Example 2: Tool Expansion with Bundles")
    print("=" * 60)

    manager = ToolsBundleManager()

    # Create two bundles
    browser_bundle = manager.create_bundle("browser")
    reasoning_bundle = manager.create_bundle("reasoning")

    # Add tools to browser bundle
    click_tool = create_mock_tool("click", "Click element")
    navigate_tool = create_mock_tool("navigate", "Navigate")
    manager.add_tool_to_bundle("browser", click_tool)
    manager.add_tool_to_bundle("browser", navigate_tool)

    # Add tools to reasoning bundle
    think_tool = create_mock_tool("think", "Think step by step")
    manager.add_tool_to_bundle("reasoning", think_tool)

    # Expand tools without bundle expansion
    print("\nWithout bundle expansion:")
    expanded = manager.expand_tools([click_tool], include_bundles=False)
    print(f"  Input: [click]")
    print(f"  Output: {[t.tool_name for t in expanded]}")

    # Expand tools with bundle expansion
    print("\nWith bundle expansion:")
    expanded = manager.expand_tools([click_tool], include_bundles=True)
    print(f"  Input: [click]")
    print(f"  Output: {[t.tool_name for t in expanded]}")


def example_bundle_filter():
    """Example 3: Using bundle filters for selective expansion."""
    print("\n" + "=" * 60)
    print("Example 3: Bundle Filters for Selective Expansion")
    print("=" * 60)

    manager = ToolsBundleManager()

    # Create bundles
    browser_bundle = manager.create_bundle("browser")
    reasoning_bundle = manager.create_bundle("reasoning")

    # Add tools
    click_tool = create_mock_tool("click", "Click")
    navigate_tool = create_mock_tool("navigate", "Navigate")
    think_tool = create_mock_tool("think", "Think")

    manager.add_tool_to_bundle("browser", click_tool)
    manager.add_tool_to_bundle("browser", navigate_tool)
    manager.add_tool_to_bundle("reasoning", think_tool)

    # Filter to only expand browser bundle
    def only_browser(bundle):
        return bundle.bundle_name == "browser"

    print("\nExpanding with filter (only browser bundle):")
    expanded = manager.expand_tools(
        [click_tool], include_bundles=True, bundle_filter=only_browser
    )
    print(f"  Input: [click]")
    print(f"  Output: {[t.tool_name for t in expanded]}")

    # Filter to exclude reasoning bundle
    def exclude_reasoning(bundle):
        return bundle.bundle_name != "reasoning"

    print("\nExpanding with filter (exclude reasoning bundle):")
    expanded = manager.expand_tools(
        [click_tool], include_bundles=True, bundle_filter=exclude_reasoning
    )
    print(f"  Input: [click]")
    print(f"  Output: {[t.tool_name for t in expanded]}")


def example_retriever_with_bundles():
    """Example 4: Using ToolsRetriever with bundles."""
    print("\n" + "=" * 60)
    print("Example 4: ToolsRetriever with Bundles")
    print("=" * 60)

    # Create a retriever with mock database
    from unittest.mock import Mock

    mock_db = Mock()
    mock_collection = Mock()
    mock_collection.clear = Mock()
    mock_collection.count = Mock(return_value=0)
    mock_collection.add = Mock()
    mock_db.get_collection = Mock(return_value=mock_collection)

    retriever = ToolsRetriever(db=mock_db)

    # Create mock tools
    click_tool = create_mock_tool("playwright_click", "Click on element")
    navigate_tool = create_mock_tool("playwright_navigate", "Navigate to URL")
    screenshot_tool = create_mock_tool("playwright_screenshot", "Take screenshot")

    # Add tools with bundle information
    retriever.add(click_tool, tool_bundle="playwright")
    retriever.add(navigate_tool, tool_bundle="playwright")
    retriever.add(screenshot_tool, tool_bundle="playwright")

    # Check bundle manager
    print(f"\nBundles in retriever: {retriever.bundle_manager.get_bundle_names()}")
    print(
        f"Tools in 'playwright' bundle: "
        f"{[t.tool_name for t in retriever.bundle_manager.get_bundle_tools('playwright')]}"
    )

    # Access bundle manager directly
    bundle = retriever.bundle_manager.get_bundle("playwright")
    print(f"\nBundle info: {bundle}")


def example_batch_add_with_bundle():
    """Example 5: Adding multiple tools to a bundle at once."""
    print("\n" + "=" * 60)
    print("Example 5: Batch Add Tools to Bundle")
    print("=" * 60)

    # Create a retriever with mock database
    from unittest.mock import Mock

    mock_db = Mock()
    mock_collection = Mock()
    mock_collection.clear = Mock()
    mock_collection.count = Mock(return_value=0)
    mock_collection.add = Mock()
    mock_db.get_collection = Mock(return_value=mock_collection)

    retriever = ToolsRetriever(db=mock_db)

    # Create multiple tools
    tools = [
        create_mock_tool("tool1", "First tool"),
        create_mock_tool("tool2", "Second tool"),
        create_mock_tool("tool3", "Third tool"),
    ]

    # Add all tools to the same bundle at once
    retriever.add_batch(tools, tool_bundle="my_bundle")

    # Verify
    bundle = retriever.bundle_manager.get_bundle("my_bundle")
    print(f"\nBundle 'my_bundle' contains {len(bundle)} tools:")
    for tool in bundle.get_all_tools():
        print(f"  - {tool.tool_name}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Tool Bundle System Examples")
    print("=" * 60)

    example_basic_bundle_usage()
    example_tool_expansion()
    example_bundle_filter()
    example_retriever_with_bundles()
    example_batch_add_with_bundle()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


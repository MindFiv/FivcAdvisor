# Tool Bundle System - Quick Start Guide

## What is the Tool Bundle System?

The Tool Bundle System preserves the association between tools from the same MCP client. When you retrieve one tool from a bundle, you can automatically get all related tools from that bundle.

## Installation

The bundle system is already integrated into FivcAdvisor. No additional installation needed.

## Basic Usage

### 1. Create a Bundle Manager

```python
from fivcadvisor.tools.types import ToolsBundleManager

manager = ToolsBundleManager()
```

### 2. Create a Bundle

```python
bundle = manager.create_bundle("playwright")
```

### 3. Add Tools to Bundle

```python
manager.add_tool_to_bundle("playwright", tool1)
manager.add_tool_to_bundle("playwright", tool2)
manager.add_tool_to_bundle("playwright", tool3)
```

### 4. Expand Tools with Bundle

```python
# Get all tools from the bundle when you have one tool
expanded_tools = manager.expand_tools(
    [tool1],
    include_bundles=True
)
# Result: [tool1, tool2, tool3]
```

## Using with ToolsRetriever

### Add Tools with Bundle

```python
from fivcadvisor.tools import ToolsRetriever

retriever = ToolsRetriever()

# Add individual tools with bundle
retriever.add(tool1, tool_bundle="playwright")
retriever.add(tool2, tool_bundle="playwright")

# Or add multiple tools at once
retriever.add_batch([tool1, tool2, tool3], tool_bundle="playwright")
```

### Retrieve with Bundle Expansion

```python
# Retrieve tools with bundle expansion
tools = retriever.retrieve(
    "click on button",
    include_bundles=True
)
# Returns: [matching_tool, ...other_tools_from_same_bundle]
```

## Advanced: Bundle Filtering

### Filter to Specific Bundles

```python
# Only expand browser-related bundles
def only_browser(bundle):
    return bundle.bundle_name.startswith("browser")

tools = retriever.retrieve(
    "click on button",
    include_bundles=True,
    bundle_filter=only_browser
)
```

### Exclude Specific Bundles

```python
# Exclude reasoning tools
def exclude_reasoning(bundle):
    return bundle.bundle_name != "reasoning"

tools = retriever.retrieve(
    "click on button",
    include_bundles=True,
    bundle_filter=exclude_reasoning
)
```

## Configuration

### YAML Configuration

```yaml
# configs/mcp.yaml
playwright:
  command: "npx"
  args: ["@playwright/mcp@latest"]
  bundle: "browser_automation"  # Optional, defaults to client name

sequential-thinking:
  command: "npx"
  args: ["@modelcontextprotocol/server-sequential-thinking"]
  bundle: "reasoning"
```

## Common Patterns

### Pattern 1: Get All Tools from a Bundle

```python
bundle = manager.get_bundle("playwright")
all_tools = bundle.get_all_tools()
```

### Pattern 2: Find Bundle by Tool

```python
tool = retriever.get_tool("playwright_click")
bundle = manager.get_bundle_by_tool(tool.tool_name)
print(f"Tool belongs to bundle: {bundle.bundle_name}")
```

### Pattern 3: Get Bundle Information

```python
info = manager.get_bundle_info("playwright")
print(f"Bundle: {info['name']}")
print(f"Tools: {info['tool_names']}")
print(f"Count: {info['tool_count']}")
```

### Pattern 4: Batch Operations

```python
# Add multiple tools to multiple bundles
tools_by_bundle = {
    "playwright": [click_tool, navigate_tool],
    "reasoning": [think_tool, analyze_tool]
}

for bundle_name, tools in tools_by_bundle.items():
    retriever.add_batch(tools, tool_bundle=bundle_name)
```

## API Reference

### ToolsBundleManager Methods

| Method | Purpose |
|--------|---------|
| `create_bundle(name, metadata)` | Create new bundle |
| `add_bundle(bundle)` | Register existing bundle |
| `get_bundle(name)` | Get bundle by name |
| `get_bundle_by_tool(tool_name)` | Find bundle containing tool |
| `add_tool_to_bundle(bundle_name, tool)` | Add tool to bundle |
| `get_bundle_tools(bundle_name)` | Get all tools in bundle |
| `expand_tools(tools, include_bundles, bundle_filter)` | Expand tool list |
| `get_bundle_info(bundle_name)` | Get bundle information |
| `cleanup()` | Clear all bundles |

### ToolsRetriever Methods (Bundle-related)

| Method | Purpose |
|--------|---------|
| `add(tool, tool_bundle)` | Add tool with optional bundle |
| `add_batch(tools, tool_bundle)` | Add multiple tools with bundle |
| `retrieve(query, include_bundles, bundle_filter)` | Retrieve with optional expansion |

## Troubleshooting

### Q: How do I know which bundle a tool belongs to?

```python
bundle = manager.get_bundle_by_tool("tool_name")
if bundle:
    print(f"Tool belongs to: {bundle.bundle_name}")
else:
    print("Tool not in any bundle")
```

### Q: How do I get all tools from a specific bundle?

```python
tools = manager.get_bundle_tools("bundle_name")
for tool in tools:
    print(tool.tool_name)
```

### Q: Can I add a tool to multiple bundles?

Currently, each tool can only belong to one bundle. If you need a tool in multiple bundles, consider:
1. Creating a shared bundle that includes both
2. Using bundle filters to include multiple bundles
3. Duplicating the tool with different names

### Q: How do I disable bundle expansion?

```python
# Don't pass include_bundles or set it to False
tools = retriever.retrieve("query")  # No expansion
# or
tools = retriever.retrieve("query", include_bundles=False)
```

## Examples

See `examples/tools/bundle_example.py` for complete working examples:

```bash
uv run python examples/tools/bundle_example.py
```

## Documentation

For detailed documentation, see:
- `docs/TOOLS_BUNDLE_SYSTEM.md` - Complete system documentation
- `tests/test_tools_bundle.py` - Test cases with usage examples

## Need Help?

1. Check the examples: `examples/tools/bundle_example.py`
2. Read the full docs: `docs/TOOLS_BUNDLE_SYSTEM.md`
3. Look at tests: `tests/test_tools_bundle.py`
4. Review the API reference above


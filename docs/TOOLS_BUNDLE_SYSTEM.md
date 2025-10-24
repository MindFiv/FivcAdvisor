# Tool Bundle System

## Overview

The Tool Bundle System is a clean, independent architecture for managing related tools from the same MCP client. It solves the problem of tool association loss when using semantic search-based tool retrieval.

### Problem Statement

When tools are loaded from MCP clients using `ToolsRetriever`, they are stored in a flat dictionary indexed by tool name. This loses the original grouping information - tools from the same MCP client (e.g., all Playwright tools) are no longer associated with each other.

When an agent needs a specific tool (e.g., "playwright_click"), it should automatically get access to all related tools from the same bundle (e.g., "playwright_navigate", "playwright_screenshot") to enable more powerful workflows.

## Architecture

### Core Components

#### 1. **ToolsBundle** (Data Model)

A lightweight data class representing a group of related tools.

```python
@dataclass
class ToolsBundle:
    bundle_name: str                    # Unique identifier
    tools: Dict[str, AgentTool]        # Tools in this bundle
    metadata: Dict[str, Any]           # Additional metadata
```

**Responsibilities:**
- Store tools belonging to a bundle
- Provide access to tools by name
- Maintain bundle metadata

#### 2. **ToolsBundleManager** (Manager)

Manages all bundles and provides operations on them.

```python
class ToolsBundleManager:
    def create_bundle(bundle_name, metadata) -> ToolsBundle
    def add_bundle(bundle) -> None
    def get_bundle(bundle_name) -> Optional[ToolsBundle]
    def get_bundle_by_tool(tool_name) -> Optional[ToolsBundle]
    def add_tool_to_bundle(bundle_name, tool) -> None
    def expand_tools(tools, include_bundles, bundle_filter) -> List[AgentTool]
    def get_bundle_info(bundle_name) -> Dict
```

**Responsibilities:**
- Create and register bundles
- Maintain tool-to-bundle mappings
- Expand tool lists with related bundle tools
- Apply filters to bundle expansion

#### 3. **ToolsRetriever** (Integration)

Enhanced to use `ToolsBundleManager` for optional bundle expansion.

**Key Changes:**
- Added `bundle_manager` parameter to `__init__`
- Enhanced `add()` and `add_batch()` to accept `tool_bundle` parameter
- Enhanced `retrieve()` to support `include_bundles` and `bundle_filter` parameters

## Design Principles

### 1. **Single Responsibility**
- `ToolsBundle`: Data storage only
- `ToolsBundleManager`: Bundle operations only
- `ToolsRetriever`: Tool retrieval and optional expansion

### 2. **Low Coupling**
- Bundle logic is completely independent
- `ToolsRetriever` uses manager through public interface
- No circular dependencies

### 3. **High Cohesion**
- All bundle-related operations in `ToolsBundleManager`
- Clear separation of concerns

### 4. **Backward Compatibility**
- All new features are optional
- Existing code works without changes
- Bundle expansion is opt-in

## Usage Examples

### Basic Bundle Creation

```python
from fivcadvisor.tools.types import ToolsBundleManager

manager = ToolsBundleManager()
bundle = manager.create_bundle("playwright")
manager.add_tool_to_bundle("playwright", tool1)
manager.add_tool_to_bundle("playwright", tool2)
```

### Tool Expansion

```python
# Without expansion
tools = manager.expand_tools([tool1], include_bundles=False)
# Returns: [tool1]

# With expansion
tools = manager.expand_tools([tool1], include_bundles=True)
# Returns: [tool1, tool2, tool3, ...]  (all tools from tool1's bundle)
```

### Bundle Filtering

```python
# Only expand specific bundles
def only_browser(bundle):
    return bundle.bundle_name == "browser"

tools = manager.expand_tools(
    [tool1],
    include_bundles=True,
    bundle_filter=only_browser
)
```

### Using with ToolsRetriever

```python
from fivcadvisor.tools import ToolsRetriever

retriever = ToolsRetriever()

# Add tools with bundle information
retriever.add(tool1, tool_bundle="playwright")
retriever.add(tool2, tool_bundle="playwright")

# Retrieve with bundle expansion
tools = retriever.retrieve(
    "click on button",
    include_bundles=True
)
```

### Batch Adding Tools

```python
# Add multiple tools to the same bundle
retriever.add_batch(
    [tool1, tool2, tool3],
    tool_bundle="playwright"
)
```

## Configuration

### YAML Configuration

```yaml
playwright:
  command: "npx"
  args: ["@playwright/mcp@latest"]
  bundle: "browser_automation"  # Optional, defaults to client name

sequential-thinking:
  command: "npx"
  args: ["@modelcontextprotocol/server-sequential-thinking"]
  bundle: "reasoning"
```

### Programmatic Configuration

```python
config = ToolsConfig("mcp.yaml")
for client_name, client_config in config._configs.items():
    bundle_name = client_config.get("bundle", client_name)
    tools = client.start().list_tools_sync()
    retriever.add_batch(tools, tool_bundle=bundle_name)
```

## API Reference

### ToolsBundle

| Method | Description |
|--------|-------------|
| `add_tool(tool)` | Add a single tool |
| `add_tools(tools)` | Add multiple tools |
| `get_tool(name)` | Get tool by name |
| `get_all_tools()` | Get all tools |
| `get_tool_names()` | Get all tool names as set |

### ToolsBundleManager

| Method | Description |
|--------|-------------|
| `create_bundle(name, metadata)` | Create new bundle |
| `add_bundle(bundle)` | Register existing bundle |
| `get_bundle(name)` | Get bundle by name |
| `get_bundle_by_tool(tool_name)` | Get bundle containing tool |
| `add_tool_to_bundle(bundle_name, tool)` | Add tool to bundle |
| `get_bundle_tools(bundle_name)` | Get all tools in bundle |
| `expand_tools(tools, include_bundles, bundle_filter)` | Expand tool list |
| `get_bundle_info(bundle_name)` | Get bundle information |
| `cleanup()` | Clear all bundles |

### ToolsRetriever

| Method | Description |
|--------|-------------|
| `add(tool, tool_bundle)` | Add tool with optional bundle |
| `add_batch(tools, tool_bundle)` | Add multiple tools with bundle |
| `retrieve(query, include_bundles, bundle_filter)` | Retrieve tools with optional expansion |

## Testing

Comprehensive test suites are provided:

- `tests/test_tools_bundle.py`: Tests for `ToolsBundle` and `ToolsBundleManager`
- `tests/test_tools_retriever.py`: Tests for `ToolsRetriever` with bundle support

Run tests:
```bash
uv run pytest tests/test_tools_bundle.py -v
uv run pytest tests/test_tools_retriever.py -v
```

## Examples

See `examples/tools/bundle_example.py` for comprehensive examples:

1. Basic bundle creation and usage
2. Tool expansion with bundles
3. Bundle filters for selective expansion
4. Using ToolsRetriever with bundles
5. Batch adding tools to bundles

Run examples:
```bash
uv run python examples/tools/bundle_example.py
```

## Future Enhancements

Possible future improvements:

1. **Tool Priority**: Mark certain tools as higher priority within a bundle
2. **Tool Dependencies**: Define dependencies between tools
3. **Conditional Bundles**: Dynamically include/exclude tools based on conditions
4. **Bundle Inheritance**: Create bundle hierarchies
5. **Tool Metadata**: Rich metadata for tools (version, compatibility, etc.)

## Files Modified/Created

### New Files
- `src/fivcadvisor/tools/types/bundles.py` - Core bundle system
- `tests/test_tools_bundle.py` - Bundle system tests
- `examples/tools/bundle_example.py` - Usage examples
- `docs/TOOLS_BUNDLE_SYSTEM.md` - This documentation

### Modified Files
- `src/fivcadvisor/tools/types/retrievers.py` - Integrated bundle manager
- `src/fivcadvisor/tools/types/configs.py` - Added bundle field validation
- `src/fivcadvisor/tools/types/__init__.py` - Exported new classes
- `src/fivcadvisor/tools/__init__.py` - Exported new classes
- `tests/test_tools_retriever.py` - Added bundle tests


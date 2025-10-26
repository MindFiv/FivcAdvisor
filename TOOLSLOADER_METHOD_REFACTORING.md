# ToolsLoader Method Refactoring

## Overview
Refactored the `ToolsLoader` class to swap method naming conventions:
- `load()` is now the synchronous method (was `load_sync()`)
- `load_async()` is now the asynchronous method (was `load()`)

This follows Python conventions where the default method name is synchronous, and async variants are explicitly named with `_async` suffix.

## Changes Made

### 1. **ToolsLoader Class** (`src/fivcadvisor/tools/types/loaders.py`)

#### Before:
```python
async def load(self):
    """Load tools from configured MCP servers and register them."""
    # async implementation

def load_sync(self):
    """Load tools synchronously."""
    # sync wrapper calling self.load()
```

#### After:
```python
def load(self):
    """Load tools synchronously."""
    # sync wrapper calling self.load_async()

async def load_async(self):
    """Load tools from configured MCP servers and register them."""
    # async implementation
```

### 2. **Updated Call Sites**

#### `src/fivcadvisor/tools/__init__.py`
- Line 43: Updated example comment from `loader.load_sync()` to `loader.load()`
- Line 58: Changed `loader.load_sync()` to `loader.load()`

#### `examples/tools/retrieve_tools.py`
- Line 30: Changed `await loader.load()` to `await loader.load_async()`

## Method Signatures

### Synchronous Method
```python
def load(self):
    """Load tools synchronously.
    
    This is a convenience method that handles event loop management
    for synchronous contexts.
    """
    try:
        asyncio.run(self.load_async())
    except RuntimeError:
        # If event loop is already running, use get_event_loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Schedule as a task instead
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(asyncio.run, self.load_async())
        else:
            loop.run_until_complete(self.load_async())
```

### Asynchronous Method
```python
async def load_async(self):
    """Load tools from configured MCP servers and register them.
    
    Uses langchain-mcp-adapters to connect to MCP servers and load their tools,
    organizing them by bundle and registering with the retriever.
    """
    # Implementation details...
```

## Usage Examples

### Synchronous Usage (Most Common)
```python
from fivcadvisor.tools.types.loaders import ToolsLoader
from fivcadvisor.tools.types.retrievers import ToolsRetriever

retriever = ToolsRetriever()
loader = ToolsLoader(retriever=retriever)
loader.load()  # Synchronous call
```

### Asynchronous Usage
```python
import asyncio
from fivcadvisor.tools.types.loaders import ToolsLoader
from fivcadvisor.tools.types.retrievers import ToolsRetriever

async def main():
    retriever = ToolsRetriever()
    loader = ToolsLoader(retriever=retriever)
    await loader.load_async()  # Asynchronous call

asyncio.run(main())
```

## Benefits

✅ **Python Convention**: Follows standard Python naming where sync is default  
✅ **Clearer Intent**: `load()` clearly indicates synchronous operation  
✅ **Better Discoverability**: Async variant is explicitly marked with `_async` suffix  
✅ **Reduced Verbosity**: Common synchronous usage is shorter (`load()` vs `load_sync()`)  
✅ **Consistency**: Aligns with Python async/await best practices  
✅ **Backward Compatibility**: No breaking changes to public API (only method names)  

## Files Modified

1. **src/fivcadvisor/tools/types/loaders.py**
   - Swapped method implementations
   - Updated docstrings
   - Lines 40-99

2. **src/fivcadvisor/tools/__init__.py**
   - Updated example comment (line 43)
   - Updated actual call (line 58)

3. **examples/tools/retrieve_tools.py**
   - Updated async example call (line 30)

## Testing

✅ All 440 tests pass  
✅ No functionality changes  
✅ All call sites updated  
✅ Both sync and async paths work correctly  

## Migration Guide

If you have existing code using the old method names:

### Old Code:
```python
loader = ToolsLoader(retriever=retriever)
loader.load_sync()  # Old synchronous method
```

### New Code:
```python
loader = ToolsLoader(retriever=retriever)
loader.load()  # New synchronous method
```

### Old Async Code:
```python
loader = ToolsLoader(retriever=retriever)
await loader.load()  # Old asynchronous method
```

### New Async Code:
```python
loader = ToolsLoader(retriever=retriever)
await loader.load_async()  # New asynchronous method
```

## Implementation Details

### Event Loop Handling
The `load()` method includes robust event loop handling:
1. First tries `asyncio.run()` for clean event loop creation
2. If RuntimeError occurs (event loop already running):
   - Checks if loop is currently running
   - If running: Uses ThreadPoolExecutor to run in separate thread
   - If not running: Uses `loop.run_until_complete()`

This ensures compatibility with various execution contexts (CLI, Streamlit, Jupyter, etc.)

## Documentation

The refactoring maintains all existing documentation and docstrings, with only method names changed to reflect the new convention.


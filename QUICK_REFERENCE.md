# Quick Reference: Persistent MCP Connections

## Problem Solved
❌ **Before**: `ClosedResourceError` when agents invoked MCP tools
✅ **After**: Tools work seamlessly with persistent connections

## Key Changes

### 1. ToolsLoader (`src/fivcadvisor/tools/types/loaders.py`)

```python
class ToolsLoader:
    # New attributes
    client: Optional[MultiServerMCPClient] = None
    sessions: Dict[str, Any] = {}
    
    # Modified method
    async def load_async(self):
        # Sessions are kept OPEN (not closed by async with)
        session = await self.client.session(bundle_name).__aenter__()
        self.sessions[bundle_name] = session
    
    # New method
    async def cleanup_async(self):
        # Close all sessions when app shuts down
        for session in self.sessions.values():
            await session.__aexit__(None, None, None)
    
    # Updated method
    def cleanup(self):
        # Synchronous wrapper
        asyncio.run(self.cleanup_async())
```

### 2. Streamlit App (`src/fivcadvisor/app/__init__.py`)

```python
@st.cache_resource
def _initialize_mcp_loader():
    """Initialize with persistent connections (cached per session)"""
    loader = default_mcp_loader
    loader.load()
    return loader

def _cleanup_mcp_loader():
    """Clean up on app shutdown"""
    loader = default_mcp_loader
    if loader.client is not None:
        loader.cleanup()

def main():
    _initialize_mcp_loader()
    atexit.register(_cleanup_mcp_loader)
    # ... rest of app
```

## Session Lifecycle

```
┌─────────────────────────────────────────┐
│ Application Startup                     │
│ ↓                                       │
│ _initialize_mcp_loader()                │
│ ├─ loader.load()                        │
│ ├─ Creates MultiServerMCPClient         │
│ ├─ Opens sessions (kept alive)          │
│ └─ Loads tools                          │
│ ↓                                       │
│ atexit.register(_cleanup_mcp_loader)    │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Agent Invokes Tools                     │
│ ├─ Tool uses open session ✅            │
│ └─ No ClosedResourceError ✅            │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Application Shutdown                    │
│ ↓                                       │
│ _cleanup_mcp_loader()                   │
│ ├─ loader.cleanup()                     │
│ ├─ Closes all sessions                  │
│ ├─ Clears client reference              │
│ └─ Removes tools from retriever         │
└─────────────────────────────────────────┘
```

## Testing

### Run All Tests
```bash
uv run pytest tests/ -q
# Result: 510 passed ✅
```

### Run ToolsLoader Tests
```bash
uv run pytest tests/test_tools_loader.py -xvs
# Result: 15 passed ✅
```

### Run Persistent Connection Tests
```bash
uv run pytest tests/test_tools_loader.py::TestToolsLoaderPersistentConnections -xvs
# Result: 3 passed ✅
```

## API Reference

### ToolsLoader Methods

| Method | Purpose | Async |
|--------|---------|-------|
| `load()` | Load tools synchronously | No |
| `load_async()` | Load tools asynchronously | Yes |
| `cleanup()` | Clean up resources synchronously | No |
| `cleanup_async()` | Clean up resources asynchronously | Yes |

### ToolsLoader Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `config` | ToolsConfig | MCP server configurations |
| `tools_retriever` | ToolsRetriever | Tool registry |
| `tools_bundles` | Dict | Tools by bundle name |
| `client` | MultiServerMCPClient | Persistent MCP client |
| `sessions` | Dict | Open MCP sessions |

## Migration Guide

### For Existing Code
✅ **No changes needed!** The implementation is backward compatible.

### For New Code
```python
from fivcadvisor.app.utils import default_mcp_loader

# Loader is automatically initialized by the app
# Just use tools normally - they work! ✅

# If you need to manually initialize:
loader = default_mcp_loader
loader.load()  # Sessions are now persistent

# When done:
loader.cleanup()  # Properly close sessions
```

## Troubleshooting

### Issue: Tools still not working
- Ensure `_initialize_mcp_loader()` is called in `main()`
- Check that MCP servers are configured in `mcp.yml`
- Verify no errors in application startup logs

### Issue: Resource leaks
- Ensure `_cleanup_mcp_loader()` is registered with `atexit`
- Check application shutdown logs for cleanup errors

### Issue: Streamlit reruns causing issues
- `@st.cache_resource` ensures single initialization per session
- Sessions are reused across reruns ✅

## Files Modified

1. `src/fivcadvisor/tools/types/loaders.py` - ToolsLoader implementation
2. `src/fivcadvisor/app/__init__.py` - Streamlit app integration
3. `tests/test_tools_loader.py` - New test cases

## Documentation

- `PERSISTENT_MCP_CONNECTIONS.md` - Detailed architecture
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `QUICK_REFERENCE.md` - This file


# Persistent MCP Connections Architecture

## Problem Statement

Previously, the FivcAdvisor application encountered `ClosedResourceError` when agents tried to invoke MCP tools. This occurred because:

1. MCP sessions were created in `ToolsLoader.load_async()` within an `async with` block
2. Tools were loaded from these sessions
3. Sessions were immediately closed when the `async with` block exited
4. When agents later tried to invoke tools, the sessions were already closed, causing `ClosedResourceError`

## Solution: Persistent Connections

The solution implements persistent MCP client and session management to keep connections alive throughout the application lifecycle.

### Architecture Overview

```
Application Startup
  ↓
main() calls _initialize_mcp_loader()
  ↓
@st.cache_resource ensures single initialization per session
  ↓
ToolsLoader.load_async()
  ├─ Creates MultiServerMCPClient
  ├─ Stores in self.client (persistent)
  ├─ Opens sessions for each server
  ├─ Stores in self.sessions (persistent)
  ├─ Loads tools from sessions
  └─ Sessions remain OPEN ✅
  ↓
Agent invokes tools
  ↓
Tools use open sessions ✅
  ↓
Application Shutdown
  ↓
atexit handler calls _cleanup_mcp_loader()
  ↓
ToolsLoader.cleanup_async()
  ├─ Closes all sessions
  ├─ Clears client reference
  └─ Removes tools from retriever
```

## Implementation Details

### 1. ToolsLoader Changes

**New Attributes:**
- `client: Optional[MultiServerMCPClient]` - Persistent MCP client
- `sessions: Dict[str, Any]` - Dictionary of open sessions by bundle name

**Modified Methods:**

#### `load_async()`
- Creates and stores `MultiServerMCPClient` in `self.client`
- Manually enters async context: `session = await client.session(bundle_name).__aenter__()`
- Stores sessions in `self.sessions` dictionary
- Sessions remain open after method returns

#### `cleanup_async()` (New)
- Asynchronously closes all open sessions
- Calls `await session.__aexit__(None, None, None)` for each session
- Clears `self.sessions` and `self.client`
- Removes all tools from retriever

#### `cleanup()` (Updated)
- Synchronous wrapper that calls `cleanup_async()` via `asyncio.run()`

### 2. Streamlit App Integration

**New Functions:**

#### `_initialize_mcp_loader()`
- Decorated with `@st.cache_resource` to ensure single initialization per session
- Calls `loader.load()` to establish persistent connections
- Returns the initialized loader

#### `_cleanup_mcp_loader()`
- Registered with `atexit` to run on application shutdown
- Safely calls `loader.cleanup()` with error handling

**Modified `main()`:**
- Calls `_initialize_mcp_loader()` to initialize persistent connections
- Registers `_cleanup_mcp_loader()` with `atexit` for cleanup

### 3. Session Lifecycle Management

**Opening Sessions:**
```python
# Manually enter async context to keep session alive
session = await self.client.session(bundle_name).__aenter__()
self.sessions[bundle_name] = session
```

**Closing Sessions:**
```python
# Manually exit async context when cleaning up
await session.__aexit__(None, None, None)
```

## Benefits

✅ **Persistent Connections** - MCP sessions remain open throughout app runtime
✅ **Tool Invocation** - Agents can successfully invoke tools without ClosedResourceError
✅ **Connection Reuse** - Better performance through connection pooling
✅ **Graceful Cleanup** - Resources properly released on application shutdown
✅ **Streamlit Compatible** - Works with Streamlit's script rerun model via caching
✅ **Error Handling** - Robust error handling for session management

## Testing

Three new test cases verify the persistent connection functionality:

1. `test_load_async_keeps_sessions_open()` - Verifies sessions are stored and not closed
2. `test_cleanup_async_closes_sessions()` - Verifies cleanup properly closes all sessions
3. `test_cleanup_sync_wrapper()` - Verifies synchronous cleanup wrapper works

All 510 tests pass, including the new persistent connection tests.

## Usage Example

```python
from fivcadvisor.app import main

# Application startup
main()

# MCP connections are now persistent
# Agents can invoke tools without ClosedResourceError

# On application shutdown:
# - atexit handler calls _cleanup_mcp_loader()
# - All MCP sessions are properly closed
# - Resources are released
```

## Migration Notes

- No changes required to existing code that uses tools
- Agents can now successfully invoke MCP tools
- The `ClosedResourceError` issue is resolved
- Application shutdown is handled automatically via `atexit`


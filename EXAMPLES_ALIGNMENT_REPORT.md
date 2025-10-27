# Examples and Docstrings Alignment Report

**Date**: 2025-10-27  
**Status**: ⚠️ ISSUES FOUND - Requires Updates  
**Severity**: HIGH - Critical imports from removed modules

---

## Executive Summary

Comprehensive audit of all example files and docstring @examples in the FivcAdvisor codebase reveals **CRITICAL ISSUES** with outdated imports and APIs that no longer exist in the current codebase.

### Key Findings:
- ❌ **2 example files** have critical import errors from removed `strands` module
- ⚠️ **1 example file** uses deprecated API patterns
- ✅ **4 example files** are properly aligned
- ✅ **Docstring examples** in source code are mostly aligned

---

## 1. Critical Issues Found

### 1.1 `examples/agents/run_agents.py` - CRITICAL ❌

**Status**: BROKEN - Will not run

**Issues**:
```python
# Line 6: REMOVED MODULE - strands no longer exists
from strands.hooks import HookRegistry, BeforeInvocationEvent, AfterInvocationEvent, MessageAddedEvent

# Line 46: DEPRECATED API - callback_handler parameter no longer supported
agent = agents.create_companion_agent(callback_handler=debugger_callback_handler)

# Line 50: DEPRECATED API - agent is not callable directly
result = agent("What time is it now?")
```

**Current Codebase**:
- `strands` module has been completely removed
- Event system moved to `fivcadvisor.events` module
- Agents use LangChain/LangGraph, not callable directly
- Use `agent.invoke()` or `agent.invoke_async()` instead

**Fix Required**: Complete rewrite using LangChain APIs

---

### 1.2 `examples/tools/retrieve_tools.py` - DEPRECATED API ⚠️

**Status**: PARTIALLY BROKEN - May fail at runtime

**Issues**:
```python
# Line 4: DEPRECATED FUNCTION - create_output_dir() signature changed
from fivcadvisor.utils import create_output_dir

# Line 25: DEPRECATED CONTEXT MANAGER - create_output_dir() no longer works as context manager
with create_output_dir():
    # This pattern is outdated
```

**Current Codebase**:
- Should use `OutputDir()` class instead
- `create_output_dir()` function exists but has different behavior

**Fix Required**: Update to use `OutputDir()` class

---

## 2. Properly Aligned Examples ✅

### 2.1 `examples/swarm_example.py` - ALIGNED ✅
- Uses `AgentsSwarmRunnable` correctly
- Imports from `fivcadvisor.agents` are correct
- LangChain integration is proper
- Async/await patterns are correct

### 2.2 `examples/tasks/task_manager_simple.py` - ALIGNED ✅
- Uses `TaskMonitorManager` correctly
- Imports from `fivcadvisor.tasks.types` are correct
- File persistence patterns are correct
- Event tracking implementation is proper

### 2.3 `examples/tasks/task_manager_advance.py` - ALIGNED ✅
- Advanced task management patterns are correct
- Multiple task handling is proper
- Statistics and filtering implementations are aligned

### 2.4 `examples/tasks/file_repository_example.py` - ALIGNED ✅
- `FileTaskRuntimeRepository` usage is correct
- Task persistence patterns are proper
- All APIs match current codebase

### 2.5 `examples/tools/bundle_example.py` - ALIGNED ✅
- Tool Bundle system usage is correct
- `ToolsRetriever` and `ToolsBundleManager` APIs are proper
- Mock tool creation patterns are aligned

---

## 3. Docstring @examples in Source Code

### 3.1 `src/fivcadvisor/agents/types/runnables.py` - ALIGNED ✅

**Module docstring example** (lines 12-30):
```python
>>> from fivcadvisor.agents.types import AgentsRunnable
>>> from langchain_openai import ChatOpenAI
>>> model = ChatOpenAI(model="gpt-4o-mini")
>>> agent = AgentsRunnable(...)
>>> result = agent.run("Hello!")
```
✅ Correct - Uses proper LangChain imports and APIs

**Class docstring example** (lines 59-81):
✅ Correct - Shows both sync and async patterns

**Method docstring example** (lines 241-255):
✅ Correct - Shows response_model usage

---

## 4. Recommended Actions

### Priority 1 - CRITICAL (Fix Immediately)
- [ ] **Fix `examples/agents/run_agents.py`**
  - Remove all `strands` imports
  - Update to use `fivcadvisor.events` module
  - Use `invoke()` / `invoke_async()` instead of calling agent directly
  - Remove `callback_handler` parameter

### Priority 2 - HIGH (Fix Soon)
- [ ] **Fix `examples/tools/retrieve_tools.py`**
  - Replace `create_output_dir()` with `OutputDir()`
  - Update context manager usage

### Priority 3 - DOCUMENTATION
- [ ] Add migration notes to examples
- [ ] Update README.md examples section
- [ ] Add deprecation warnings to old patterns

---

## 5. Testing Recommendations

After fixes, run:
```bash
# Test all examples
python examples/agents/run_agents.py
python examples/tools/retrieve_tools.py
python examples/swarm_example.py
python examples/tasks/task_manager_simple.py
python examples/tasks/task_manager_advance.py
python examples/tools/bundle_example.py
python examples/tasks/file_repository_example.py

# Run full test suite
pytest tests/ -v
```

---

## Summary Table

| File | Status | Issues | Action |
|------|--------|--------|--------|
| `examples/agents/run_agents.py` | ❌ BROKEN | Strands imports, deprecated APIs | REWRITE |
| `examples/tools/retrieve_tools.py` | ⚠️ PARTIAL | Deprecated OutputDir usage | UPDATE |
| `examples/swarm_example.py` | ✅ OK | None | NONE |
| `examples/tasks/task_manager_simple.py` | ✅ OK | None | NONE |
| `examples/tasks/task_manager_advance.py` | ✅ OK | None | NONE |
| `examples/tasks/file_repository_example.py` | ✅ OK | None | NONE |
| `examples/tools/bundle_example.py` | ✅ OK | None | NONE |
| Docstring @examples | ✅ OK | None | NONE |

---

**Next Steps**: See detailed fix recommendations in sections 1.1 and 1.2


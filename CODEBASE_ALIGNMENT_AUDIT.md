# FivcAdvisor Codebase Alignment Audit

**Date**: 2025-10-27  
**Audit Type**: Examples and Docstrings Alignment Check  
**Overall Status**: ⚠️ ISSUES FOUND - 2 Critical, 1 High Priority

---

## Executive Summary

Complete audit of all example files and docstring @examples in FivcAdvisor codebase:

- **Total Example Files**: 7
- **Properly Aligned**: 5 ✅
- **Requires Updates**: 2 ⚠️
- **Docstring Examples**: All Aligned ✅

---

## Critical Issues

### Issue #1: `examples/agents/run_agents.py` - BROKEN ❌

**Severity**: CRITICAL  
**Impact**: Example will not run - ImportError

**Problems**:
1. **Line 6**: Imports from removed `strands` module
   ```python
   from strands.hooks import HookRegistry, BeforeInvocationEvent, ...
   ```
   - `strands` module no longer exists
   - Replaced by `fivcadvisor.events` module

2. **Line 46**: Uses deprecated `callback_handler` parameter
   ```python
   agent = agents.create_companion_agent(callback_handler=...)
   ```
   - Parameter no longer supported in LangChain agents

3. **Line 50**: Calls agent as function
   ```python
   result = agent("What time is it now?")
   ```
   - Agents are not callable
   - Use `agent.invoke()` or `agent.invoke_async()`

**Fix**: Complete rewrite using LangChain/LangGraph APIs

---

### Issue #2: `examples/tools/retrieve_tools.py` - DEPRECATED API ⚠️

**Severity**: HIGH  
**Impact**: May fail at runtime - API mismatch

**Problems**:
1. **Line 4**: Uses deprecated function
   ```python
   from fivcadvisor.utils import create_output_dir
   ```

2. **Line 25**: Incorrect context manager usage
   ```python
   with create_output_dir():
       # This pattern is outdated
   ```
   - Should use `OutputDir()` class instead
   - See `examples/tasks/task_manager_simple.py` for correct pattern

**Fix**: Update to use `OutputDir()` class

---

## Properly Aligned Examples ✅

### 1. `examples/swarm_example.py` ✅
- ✅ Uses `AgentsSwarmRunnable` correctly
- ✅ LangChain imports are proper
- ✅ Async patterns are correct
- ✅ Tool definitions are aligned

### 2. `examples/tasks/task_manager_simple.py` ✅
- ✅ Uses `TaskMonitorManager` correctly
- ✅ File persistence patterns are proper
- ✅ Event tracking is aligned
- ✅ All imports are current

### 3. `examples/tasks/task_manager_advance.py` ✅
- ✅ Advanced task management is correct
- ✅ Multiple task handling is proper
- ✅ Statistics and filtering are aligned

### 4. `examples/tasks/file_repository_example.py` ✅
- ✅ `FileTaskRuntimeRepository` usage is correct
- ✅ Task persistence patterns are proper
- ✅ All APIs match current codebase

### 5. `examples/tools/bundle_example.py` ✅
- ✅ Tool Bundle system usage is correct
- ✅ `ToolsRetriever` and `ToolsBundleManager` are proper
- ✅ Mock patterns are aligned

---

## Docstring Examples Status ✅

**All docstring @examples are properly aligned**

### Verified Locations:
- ✅ `src/fivcadvisor/agents/types/runnables.py` - Module docstring
- ✅ `src/fivcadvisor/agents/types/runnables.py` - Class docstring
- ✅ `src/fivcadvisor/agents/types/runnables.py` - Method docstring

**Key Points**:
- All use current LangChain APIs
- No references to removed modules
- All imports are correct
- All method signatures match implementation

---

## Action Items

### Priority 1 - CRITICAL (Fix Immediately)
- [ ] Rewrite `examples/agents/run_agents.py`
  - Remove all `strands` imports
  - Use `fivcadvisor.events` module
  - Use `invoke()` / `invoke_async()` methods
  - Remove `callback_handler` parameter

### Priority 2 - HIGH (Fix Soon)
- [ ] Update `examples/tools/retrieve_tools.py`
  - Replace `create_output_dir()` with `OutputDir()`
  - Update context manager usage

### Priority 3 - DOCUMENTATION
- [ ] Add migration notes to examples
- [ ] Update README.md examples section
- [ ] Add deprecation warnings

---

## Testing Plan

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

# Run doctests
pytest --doctest-modules src/ -v
```

---

## Summary Table

| File | Status | Issues | Priority |
|------|--------|--------|----------|
| `examples/agents/run_agents.py` | ❌ BROKEN | Strands imports, deprecated APIs | CRITICAL |
| `examples/tools/retrieve_tools.py` | ⚠️ PARTIAL | Deprecated OutputDir usage | HIGH |
| `examples/swarm_example.py` | ✅ OK | None | - |
| `examples/tasks/task_manager_simple.py` | ✅ OK | None | - |
| `examples/tasks/task_manager_advance.py` | ✅ OK | None | - |
| `examples/tasks/file_repository_example.py` | ✅ OK | None | - |
| `examples/tools/bundle_example.py` | ✅ OK | None | - |
| Docstring @examples | ✅ OK | None | - |

---

## Related Documents

- `EXAMPLES_ALIGNMENT_REPORT.md` - Detailed example analysis
- `DOCSTRING_EXAMPLES_VERIFICATION.md` - Docstring verification details

---

**Audit Completed**: 2025-10-27  
**Next Review**: After implementing fixes


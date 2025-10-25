# Strands 移除 - 快速参考指南

## 🎯 一页纸总结

### 现状
- **26 处** strands 导入
- **13 个** 受影响文件
- **3 个** 新增兼容文件
- **5-8 天** 预计工作量

### 迁移路径
```
类型系统 → 工具系统 → Agent/Swarm → Hook系统 → 清理测试
```

---

## 📝 导入替换速查表

### 第1阶段: 类型系统

```python
# 旧
from strands.types.content import Message
from strands.types.content import ContentBlock
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolUse, ToolResult
from strands.multiagent.base import Status as TaskStatus

# 新
from fivcadvisor.types.compat import Message, ContentBlock, StreamEvent, ToolUse, ToolResult
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
```

### 第2阶段: 工具系统

```python
# 旧
from strands.types.tools import AgentTool
from strands.tools import tool as make_tool
from strands.tools.mcp import MCPClient
from strands.types.exceptions import MCPClientInitializationError
from strands.tools.registry import ToolRegistry

# 新
from fivcadvisor.tools.compat import AgentTool, tool as make_tool, MCPClientInitializationError
# MCPClient: 使用 mcp 库或自定义实现
# ToolRegistry: 创建自定义或使用 LangChain
```

### 第3阶段: Agent/Swarm

```python
# 旧
from strands.agent import Agent
from strands.multiagent import Swarm
from strands.agent import AgentResult, SlidingWindowConversationManager

# 新
from fivcadvisor.adapters import LangChainAgentAdapter, LangGraphSwarmAdapter
# AgentResult: 定义本地类型或使用 dict
# SlidingWindowConversationManager: 创建自定义实现
```

### 第4阶段: Hook 系统

```python
# 旧
from strands.hooks import HookRegistry, HookEvent, BeforeInvocationEvent, AfterInvocationEvent, MessageAddedEvent

# 新
from fivcadvisor.events.hooks import HookRegistry, HookEvent
# 事件类型: 定义为字符串常量或 Enum
```

---

## 🔧 新增文件模板

### 1. `src/fivcadvisor/types/compat.py`

```python
"""Type compatibility layer for Strands → LangChain migration."""

from langchain_core.messages import BaseMessage
from typing import Any, Dict, Union

# Message type
Message = Union[BaseMessage, Dict[str, Any]]

# Content block
ContentBlock = Dict[str, Any]

# Tool types
ToolUse = Dict[str, Any]
ToolResult = Dict[str, Any]

# Stream event
class StreamEvent:
    """Represents a streaming event."""
    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data
```

### 2. `src/fivcadvisor/tools/compat.py`

```python
"""Tool compatibility layer for Strands → LangChain migration."""

from langchain_core.tools import Tool, tool

# Tool type
AgentTool = Tool

# Tool decorator
__all__ = ['AgentTool', 'tool']

# Exception
class MCPClientInitializationError(Exception):
    """Raised when MCP client initialization fails."""
    pass
```

### 3. `src/fivcadvisor/events/hooks.py`

```python
"""Custom event system for Strands → LangChain migration."""

from typing import Callable, Dict, List, Any
from enum import Enum

class HookEvent:
    """Base event class."""
    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data

class HookRegistry:
    """Event registry for hook-based execution tracking."""
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register(self, event_type: str, callback: Callable):
        """Register a callback for an event type."""
        if event_type not in self.hooks:
            self.hooks[event_type] = []
        self.hooks[event_type].append(callback)
    
    def emit(self, event: HookEvent):
        """Emit an event to all registered callbacks."""
        for callback in self.hooks.get(event.event_type, []):
            try:
                callback(event)
            except Exception as e:
                print(f"Error in hook callback: {e}")
```

---

## 🧪 测试命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定阶段的测试
pytest tests/test_agents_runtime.py -v          # 第1阶段
pytest tests/test_tools_*.py -v                 # 第2阶段
pytest tests/test_langchain_agents_adapter.py -v # 第3阶段
pytest tests/test_task_monitor.py -v            # 第4阶段

# 检查覆盖率
pytest tests/ --cov=src/fivcadvisor --cov-report=html

# 类型检查
mypy src/fivcadvisor

# Linting
pylint src/fivcadvisor
```

---

## 📋 文件修改清单

### 第1阶段 (5 个文件)

- [ ] `src/fivcadvisor/agents/types/base.py` - 第 58 行
- [ ] `src/fivcadvisor/tasks/types/base.py` - 第 21-22 行
- [ ] `src/fivcadvisor/app/components/chat_message.py` - 第 4 行
- [ ] `src/fivcadvisor/app/views/chats.py` - 第 23 行
- [ ] `src/fivcadvisor/adapters/agents.py` - 第 25 行

### 第2阶段 (4 个文件)

- [ ] `src/fivcadvisor/tools/types/configs.py` - 第 6 行
- [ ] `src/fivcadvisor/tools/types/bundles.py` - 第 11 行
- [ ] `src/fivcadvisor/tools/types/retrievers.py` - 第 4-5 行
- [ ] `src/fivcadvisor/tools/__init__.py` - 第 15, 29-30 行

### 第3阶段 (4 个文件)

- [ ] `src/fivcadvisor/agents/__init__.py` - 第 19-20 行
- [ ] `src/fivcadvisor/agents/types/monitors.py` - 第 33-37 行
- [ ] `src/fivcadvisor/agents/types/retrievers.py` - 第 3-4 行
- [ ] `src/fivcadvisor/tasks/types/monitors.py` - 第 25-34 行

### 第4阶段 (1 个文件)

- [ ] `src/fivcadvisor/tasks/types/monitors.py` - 第 26-33 行 (Hook 导入)

### 第5阶段 (1 个文件)

- [ ] `pyproject.toml` - 移除 strands 依赖

---

## 🚀 快速开始

### 1. 准备 (5 分钟)

```bash
# 创建分支
git checkout -b feature/remove-strands

# 确保测试通过
pytest tests/ -v
```

### 2. 创建兼容层 (15 分钟)

```bash
# 创建目录
mkdir -p src/fivcadvisor/types
mkdir -p src/fivcadvisor/events

# 创建文件 (使用上面的模板)
touch src/fivcadvisor/types/__init__.py
touch src/fivcadvisor/types/compat.py
touch src/fivcadvisor/tools/compat.py
touch src/fivcadvisor/events/__init__.py
touch src/fivcadvisor/events/hooks.py
```

### 3. 逐阶段迁移 (5-8 天)

按照 `STRANDS_REMOVAL_CHECKLIST.md` 逐步执行

### 4. 验证 (1 天)

```bash
# 运行所有测试
pytest tests/ -v

# 检查覆盖率
pytest tests/ --cov=src/fivcadvisor

# 类型检查
mypy src/fivcadvisor

# 启动 Web 界面
streamlit run src/fivcadvisor/app/main.py
```

---

## 💡 常见问题

### Q: 如何处理 AgentResult?
A: 定义本地类型或使用 dict，根据实际使用情况调整

### Q: MCPClient 如何替换?
A: 使用 mcp 库直接或创建自定义包装

### Q: Hook 系统如何工作?
A: 使用自定义 HookRegistry 和事件类型

### Q: 如何验证迁移完成?
A: 所有测试通过 + 类型检查通过 + Web 界面正常

---

## 📞 需要帮助?

参考完整文档:
- `STRANDS_REMOVAL_PLAN.md` - 详细计划
- `STRANDS_REMOVAL_IMPLEMENTATION.md` - 实施指南
- `STRANDS_REMOVAL_FILE_MAPPING.md` - 文件映射
- `STRANDS_REMOVAL_CHECKLIST.md` - 执行清单


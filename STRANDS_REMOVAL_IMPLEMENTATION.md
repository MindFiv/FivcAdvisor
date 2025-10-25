# Strands 移除实施指南

## 第1阶段: 替换类型系统

### 1.1 创建兼容层 (新文件)

创建 `src/fivcadvisor/types/compat.py` 来定义兼容类型:

```python
# 消息类型兼容
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import Union, List, Dict, Any

# 定义兼容的 Message 类型
Message = Union[BaseMessage, Dict[str, Any]]

# 工具调用兼容
from langchain_core.tools import ToolCall

ToolUse = ToolCall
ToolResult = Dict[str, Any]

# 流事件兼容
class StreamEvent:
    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data
```

### 1.2 更新导入

**文件**: `src/fivcadvisor/agents/types/base.py`
```python
# 旧: from strands.types.content import Message
# 新: from fivcadvisor.types.compat import Message
```

**文件**: `src/fivcadvisor/tasks/types/base.py`
```python
# 旧: from strands.types.content import Message
# 新: from fivcadvisor.types.compat import Message

# 旧: from strands.multiagent.base import Status as TaskStatus
# 新: 定义本地 TaskStatus enum
```

### 1.3 定义本地 TaskStatus

在 `src/fivcadvisor/tasks/types/base.py` 中:

```python
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## 第2阶段: 替换工具系统

### 2.1 创建工具兼容层

创建 `src/fivcadvisor/tools/compat.py`:

```python
from langchain_core.tools import Tool, tool
from typing import Any, Dict, Callable

# 导出 LangChain 的 tool decorator
__all__ = ['Tool', 'tool']

# AgentTool 兼容
AgentTool = Tool

# MCPClientInitializationError 兼容
class MCPClientInitializationError(Exception):
    pass
```

### 2.2 更新工具导入

**文件**: `src/fivcadvisor/tools/types/bundles.py`
```python
# 旧: from strands.types.tools import AgentTool
# 新: from fivcadvisor.tools.compat import AgentTool
```

**文件**: `src/fivcadvisor/tools/types/retrievers.py`
```python
# 旧: from strands.types.tools import AgentTool
# 新: from fivcadvisor.tools.compat import AgentTool

# 旧: from strands.tools import tool as make_tool
# 新: from fivcadvisor.tools.compat import tool as make_tool
```

### 2.3 处理 MCPClient

**文件**: `src/fivcadvisor/tools/types/configs.py`

需要创建自定义 MCPClient 或使用现有的 MCP 库:

```python
# 旧: from strands.tools.mcp import MCPClient
# 新: 使用 mcp 库直接或创建自定义包装
```

### 2.4 处理 ToolRegistry

**文件**: `src/fivcadvisor/tools/__init__.py`

```python
# 旧: from strands.tools.registry import ToolRegistry
# 新: 创建自定义 ToolRegistry 或使用 LangChain 的工具管理
```

---

## 第3阶段: 替换 Agent 和 Swarm

### 3.1 更新类型注解

**文件**: `src/fivcadvisor/agents/types/retrievers.py`

```python
# 旧: from strands.agent import Agent
# 新: from fivcadvisor.adapters import LangChainAgentAdapter

# 旧: from strands.multiagent import MultiAgentBase
# 新: from fivcadvisor.adapters import LangGraphSwarmAdapter

# 更新类型注解
def __call__(self, *args, **kwargs) -> Union[LangChainAgentAdapter, LangGraphSwarmAdapter, Any]:
    ...
```

### 3.2 移除导入

**文件**: `src/fivcadvisor/agents/__init__.py`

```python
# 移除这两行:
# from strands.agent import Agent
# from strands.multiagent import Swarm

# 更新返回类型注解
def create_default_agent(*args, **kwargs) -> LangChainAgentAdapter:
    ...

def create_generic_agent_swarm(...) -> LangGraphSwarmAdapter:
    ...
```

---

## 第4阶段: 替换 Hook 系统

### 4.1 创建事件系统

创建 `src/fivcadvisor/events/hooks.py`:

```python
from typing import Callable, Dict, List, Any
from enum import Enum

class HookEvent:
    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data

class HookRegistry:
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register(self, event_type: str, callback: Callable):
        if event_type not in self.hooks:
            self.hooks[event_type] = []
        self.hooks[event_type].append(callback)
    
    def emit(self, event: HookEvent):
        for callback in self.hooks.get(event.event_type, []):
            callback(event)
```

### 4.2 更新 TaskMonitor

**文件**: `src/fivcadvisor/tasks/types/monitors.py`

```python
# 旧: from strands.hooks import HookRegistry, ...
# 新: from fivcadvisor.events.hooks import HookRegistry, ...
```

---

## 第5阶段: 清理和测试

### 5.1 移除依赖

编辑 `pyproject.toml`:
```toml
# 移除: strands = "..."
# 移除: strands-tools = "..."
```

### 5.2 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_agents_runtime.py -v
pytest tests/test_langchain_agents_adapter.py -v
```

### 5.3 验证功能

- [ ] 启动 Web 界面
- [ ] 测试聊天功能
- [ ] 测试任务执行
- [ ] 测试工具调用

---

## 📝 检查清单

### 第1阶段
- [ ] 创建 `src/fivcadvisor/types/compat.py`
- [ ] 更新 5 个文件的导入
- [ ] 定义本地 `TaskStatus`
- [ ] 运行类型检查

### 第2阶段
- [ ] 创建 `src/fivcadvisor/tools/compat.py`
- [ ] 更新 4 个工具文件的导入
- [ ] 处理 MCPClient
- [ ] 处理 ToolRegistry

### 第3阶段
- [ ] 更新类型注解
- [ ] 移除 Agent/Swarm 导入
- [ ] 验证适配器工作

### 第4阶段
- [ ] 创建事件系统
- [ ] 更新 TaskMonitor
- [ ] 测试 Hook 功能

### 第5阶段
- [ ] 从 pyproject.toml 移除依赖
- [ ] 运行所有测试
- [ ] 验证 Web 界面
- [ ] 最终检查


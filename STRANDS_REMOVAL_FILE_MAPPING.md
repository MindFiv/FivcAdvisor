# Strands 移除 - 文件映射表

## 📋 完整的文件和导入映射

### 第1阶段: 类型系统 (5 个文件)

#### 1. `src/fivcadvisor/agents/types/base.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 58 | `from strands.types.content import Message` | `from fivcadvisor.types.compat import Message` | 消息类型 |

**影响的类/函数**:
- `AgentsRuntimeMeta` - 使用 Message 类型
- `AgentsRuntime` - 使用 Message 类型

---

#### 2. `src/fivcadvisor/tasks/types/base.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 21 | `from strands.types.content import Message` | `from fivcadvisor.types.compat import Message` | 消息类型 |
| 22 | `from strands.multiagent.base import Status as TaskStatus` | 本地定义 | 任务状态 |

**影响的类/函数**:
- `TaskRuntimeStep` - 使用 Message 类型
- `TaskRuntime` - 使用 TaskStatus

**新增代码**:
```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

#### 3. `src/fivcadvisor/app/components/chat_message.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 4 | `from strands.types.content import Message` | `from fivcadvisor.types.compat import Message` | 消息类型 |

**影响的类/函数**:
- `ChatMessage` - 使用 Message 类型

---

#### 4. `src/fivcadvisor/app/views/chats.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 23 | `from strands.types.content import Message, ContentBlock` | `from fivcadvisor.types.compat import Message, ContentBlock` | 消息和内容块 |

**影响的类/函数**:
- `ChatView.render()` - 使用 Message 和 ContentBlock

---

#### 5. `src/fivcadvisor/adapters/agents.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 25 | `from strands.types.content import Message, ContentBlock` | `from fivcadvisor.types.compat import Message, ContentBlock` | 消息和内容块 |

**影响的类/函数**:
- `LangChainAgentAdapter` - 使用 Message 和 ContentBlock

---

### 第2阶段: 工具系统 (4 个文件)

#### 6. `src/fivcadvisor/tools/types/configs.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 6 | `from strands.tools.mcp import MCPClient` | 自定义或 mcp 库 | MCP 客户端 |

**影响的类/函数**:
- `ToolsConfigValue.get_client()` - 返回 MCPClient

**选项**:
- 使用 `mcp` 库直接
- 创建自定义 MCPClient 包装

---

#### 7. `src/fivcadvisor/tools/types/bundles.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 11 | `from strands.types.tools import AgentTool` | `from fivcadvisor.tools.compat import AgentTool` | 工具类型 |

**影响的类/函数**:
- `ToolsBundle` - 使用 AgentTool 类型

---

#### 8. `src/fivcadvisor/tools/types/retrievers.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 4 | `from strands.types.tools import AgentTool` | `from fivcadvisor.tools.compat import AgentTool` | 工具类型 |
| 5 | `from strands.tools import tool as make_tool` | `from fivcadvisor.tools.compat import tool as make_tool` | 工具装饰器 |

**影响的类/函数**:
- `ToolsRetriever` - 使用 AgentTool 类型

---

#### 9. `src/fivcadvisor/tools/__init__.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 15 | `from strands.types.exceptions import MCPClientInitializationError` | `from fivcadvisor.tools.compat import MCPClientInitializationError` | 异常类型 |
| 29 | `from strands.tools.registry import ToolRegistry` | 自定义或 LangChain | 工具注册表 |
| 30 | `from strands_tools import (...)` | 自定义工具或 LangChain | 默认工具 |

**影响的函数**:
- `register_default_tools()` - 使用 ToolRegistry
- `register_mcp_tools()` - 使用 MCPClientInitializationError

---

### 第3阶段: Agent/Swarm (4 个文件)

#### 10. `src/fivcadvisor/agents/__init__.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 19 | `from strands.agent import Agent` | 移除 | 使用 LangChainAgentAdapter |
| 20 | `from strands.multiagent import Swarm` | 移除 | 使用 LangGraphSwarmAdapter |

**影响的函数**:
- `create_default_agent()` - 返回类型改为 `LangChainAgentAdapter`
- `create_generic_agent_swarm()` - 返回类型改为 `LangGraphSwarmAdapter`

---

#### 11. `src/fivcadvisor/agents/types/monitors.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 33 | `from strands import Agent` | 移除 | 使用 LangChainAgentAdapter |
| 34 | `from strands.agent import AgentResult, SlidingWindowConversationManager` | 自定义 | 代理结果和会话管理 |
| 35 | `from strands.types.content import Message` | `from fivcadvisor.types.compat import Message` | 消息类型 |
| 36 | `from strands.types.streaming import StreamEvent` | `from fivcadvisor.types.compat import StreamEvent` | 流事件 |
| 37 | `from strands.types.tools import ToolUse, ToolResult` | `from fivcadvisor.types.compat import ToolUse, ToolResult` | 工具调用 |

**影响的类**:
- `AgentsMonitor` - 使用所有这些类型

---

#### 12. `src/fivcadvisor/agents/types/retrievers.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 3 | `from strands.agent import Agent` | 移除 | 使用 LangChainAgentAdapter |
| 4 | `from strands.multiagent import MultiAgentBase` | 移除 | 使用 LangGraphSwarmAdapter |

**影响的类**:
- `AgentsCreatorBase` - 返回类型改为 Union[LangChainAgentAdapter, LangGraphSwarmAdapter, Any]

---

#### 13. `src/fivcadvisor/tasks/types/monitors.py`
| 行号 | 旧导入 | 新导入 | 说明 |
|------|--------|--------|------|
| 25 | `from strands import Agent` | 移除 | 使用 LangChainAgentAdapter |
| 26-33 | `from strands.hooks import (...)` | `from fivcadvisor.events.hooks import (...)` | 事件系统 |
| 34 | `from strands.multiagent import MultiAgentBase` | 移除 | 使用 LangGraphSwarmAdapter |

---

### 第4阶段: Hook 系统 (1 个文件)

#### 14. `src/fivcadvisor/tasks/types/monitors.py` (续)
- 已在第3阶段处理

---

### 第5阶段: 清理

#### 15. `pyproject.toml`
移除以下依赖:
```toml
strands = "..."
strands-tools = "..."
```

---

## 🔗 新增文件

### 1. `src/fivcadvisor/types/compat.py` (新建)
```python
# 类型兼容层
from langchain_core.messages import BaseMessage
from typing import Any, Dict, Union

Message = Union[BaseMessage, Dict[str, Any]]
ContentBlock = Dict[str, Any]
ToolUse = Dict[str, Any]
ToolResult = Dict[str, Any]

class StreamEvent:
    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data
```

### 2. `src/fivcadvisor/tools/compat.py` (新建)
```python
# 工具兼容层
from langchain_core.tools import Tool, tool

AgentTool = Tool

class MCPClientInitializationError(Exception):
    pass
```

### 3. `src/fivcadvisor/events/hooks.py` (新建)
```python
# 事件系统
from typing import Callable, Dict, List, Any

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

---

## 📊 变更统计

| 类别 | 文件数 | 导入数 | 新增文件 |
|------|--------|--------|---------|
| 第1阶段 | 5 | 5 | 1 |
| 第2阶段 | 4 | 4 | 1 |
| 第3阶段 | 4 | 7 | 0 |
| 第4阶段 | 1 | 3 | 1 |
| 第5阶段 | 1 | 0 | 0 |
| **总计** | **13** | **26** | **3** |


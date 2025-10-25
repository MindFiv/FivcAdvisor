# Strands 移除 - 代码示例

## 第1阶段: 类型系统示例

### 示例 1: 更新 `src/fivcadvisor/agents/types/base.py`

**旧代码**:
```python
from strands.types.content import Message

class AgentsRuntimeMeta(BaseModel):
    messages: List[Message] = Field(default_factory=list)
```

**新代码**:
```python
from fivcadvisor.types.compat import Message

class AgentsRuntimeMeta(BaseModel):
    messages: List[Message] = Field(default_factory=list)
```

### 示例 2: 定义本地 TaskStatus

**旧代码**:
```python
from strands.multiagent.base import Status as TaskStatus

class TaskRuntime(BaseModel):
    status: TaskStatus = TaskStatus.PENDING
```

**新代码**:
```python
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskRuntime(BaseModel):
    status: TaskStatus = TaskStatus.PENDING
```

---

## 第2阶段: 工具系统示例

### 示例 3: 更新工具导入

**旧代码**:
```python
from strands.types.tools import AgentTool
from strands.tools import tool as make_tool

class ToolsBundle:
    tools: Dict[str, AgentTool] = field(default_factory=dict)
    
    def add_tool(self, tool: AgentTool) -> None:
        self.tools[tool.tool_name] = tool
```

**新代码**:
```python
from fivcadvisor.tools.compat import AgentTool, tool as make_tool

class ToolsBundle:
    tools: Dict[str, AgentTool] = field(default_factory=dict)
    
    def add_tool(self, tool: AgentTool) -> None:
        self.tools[tool.tool_name] = tool
```

### 示例 4: 处理异常

**旧代码**:
```python
from strands.types.exceptions import MCPClientInitializationError

try:
    client = client_config.get_client()
except MCPClientInitializationError as e:
    print(f"Error: {e}")
```

**新代码**:
```python
from fivcadvisor.tools.compat import MCPClientInitializationError

try:
    client = client_config.get_client()
except MCPClientInitializationError as e:
    print(f"Error: {e}")
```

---

## 第3阶段: Agent/Swarm 示例

### 示例 5: 更新 Agent 创建

**旧代码**:
```python
from strands.agent import Agent

def create_default_agent(*args, **kwargs) -> Agent:
    agent = create_langchain_agent(*args, **kwargs)
    return agent
```

**新代码**:
```python
from fivcadvisor.adapters import LangChainAgentAdapter

def create_default_agent(*args, **kwargs) -> LangChainAgentAdapter:
    agent = create_langchain_agent(*args, **kwargs)
    return agent
```

### 示例 6: 更新 Swarm 创建

**旧代码**:
```python
from strands.multiagent import Swarm

def create_generic_agent_swarm(...) -> Swarm:
    return LangGraphSwarmAdapter(s_agents)
```

**新代码**:
```python
from fivcadvisor.adapters import LangGraphSwarmAdapter

def create_generic_agent_swarm(...) -> LangGraphSwarmAdapter:
    return LangGraphSwarmAdapter(s_agents)
```

### 示例 7: 更新类型注解

**旧代码**:
```python
from strands.agent import Agent
from strands.multiagent import MultiAgentBase

class AgentsCreatorBase(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> Union[Agent, MultiAgentBase, Any]:
        raise NotImplementedError()
```

**新代码**:
```python
from fivcadvisor.adapters import LangChainAgentAdapter, LangGraphSwarmAdapter

class AgentsCreatorBase(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> Union[LangChainAgentAdapter, LangGraphSwarmAdapter, Any]:
        raise NotImplementedError()
```

---

## 第4阶段: Hook 系统示例

### 示例 8: 创建事件系统

**旧代码**:
```python
from strands.hooks import HookRegistry, BeforeInvocationEvent, AfterInvocationEvent

registry = HookRegistry()
registry.register(BeforeInvocationEvent, callback)
```

**新代码**:
```python
from fivcadvisor.events.hooks import HookRegistry, HookEvent

registry = HookRegistry()
registry.register("before_invocation", callback)

# 触发事件
event = HookEvent("before_invocation", {"agent_id": "123"})
registry.emit(event)
```

### 示例 9: 更新 TaskMonitor

**旧代码**:
```python
from strands.hooks import HookRegistry, MessageAddedEvent

class TaskMonitor:
    def __init__(self):
        self.hooks = HookRegistry()
    
    def on_message_added(self, event: MessageAddedEvent):
        # 处理消息
        pass
```

**新代码**:
```python
from fivcadvisor.events.hooks import HookRegistry, HookEvent

class TaskMonitor:
    def __init__(self):
        self.hooks = HookRegistry()
        self.hooks.register("message_added", self.on_message_added)
    
    def on_message_added(self, event: HookEvent):
        # 处理消息
        data = event.data
        pass
```

---

## 第5阶段: 清理示例

### 示例 10: 更新 pyproject.toml

**旧代码**:
```toml
[project]
dependencies = [
    "langchain>=0.1.0",
    "langchain-core>=0.1.0",
    "strands>=0.1.0",
    "strands-tools>=0.1.0",
    "strands_tools>=0.1.0",
]
```

**新代码**:
```toml
[project]
dependencies = [
    "langchain>=0.1.0",
    "langchain-core>=0.1.0",
    "langchain-openai>=0.1.0",
    "langgraph>=0.1.0",
]
```

---

## 完整迁移示例

### 示例 11: 完整的文件迁移

**文件**: `src/fivcadvisor/agents/types/monitors.py`

**旧代码** (第 33-37 行):
```python
from strands import Agent
from strands.agent import AgentResult, SlidingWindowConversationManager
from strands.types.content import Message
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolUse, ToolResult
```

**新代码**:
```python
from fivcadvisor.types.compat import Message, StreamEvent, ToolUse, ToolResult
from fivcadvisor.adapters import LangChainAgentAdapter

# 定义本地类型
class AgentResult(BaseModel):
    """Agent execution result."""
    output: str
    messages: List[Message] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)

class SlidingWindowConversationManager:
    """Manages conversation history with sliding window."""
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.messages: List[Message] = []
    
    def add_message(self, message: Message):
        self.messages.append(message)
        if len(self.messages) > self.window_size:
            self.messages = self.messages[-self.window_size:]
```

---

## 测试示例

### 示例 12: 测试兼容层

```python
# tests/test_types_compat.py

from fivcadvisor.types.compat import Message, StreamEvent, ToolUse, ToolResult

def test_message_type():
    """Test Message type compatibility."""
    msg = {"role": "user", "content": "Hello"}
    assert isinstance(msg, dict)

def test_stream_event():
    """Test StreamEvent class."""
    event = StreamEvent("text", "Hello")
    assert event.event_type == "text"
    assert event.data == "Hello"

def test_tool_use():
    """Test ToolUse type."""
    tool_use = {"tool_name": "calculator", "input": "2+2"}
    assert tool_use["tool_name"] == "calculator"
```

---

## 验证清单

### 导入验证

```bash
# 验证新导入可用
python -c "from fivcadvisor.types.compat import Message; print('✓ Message')"
python -c "from fivcadvisor.tools.compat import AgentTool; print('✓ AgentTool')"
python -c "from fivcadvisor.events.hooks import HookRegistry; print('✓ HookRegistry')"
```

### 类型检查

```bash
# 运行 mypy
mypy src/fivcadvisor/types/compat.py
mypy src/fivcadvisor/tools/compat.py
mypy src/fivcadvisor/events/hooks.py
```

### 测试验证

```bash
# 运行相关测试
pytest tests/test_agents_runtime.py -v
pytest tests/test_tools_*.py -v
pytest tests/test_task_monitor.py -v
```


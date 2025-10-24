# Strands → LangChain 详细迁移计划

---

## 📐 架构设计

### 新的适配层结构
```
src/fivcadvisor/
├── adapters/                    # 新增: LangChain 适配层
│   ├── __init__.py
│   ├── models.py               # LangChain 模型包装
│   ├── agents.py               # Agent 创建和管理
│   ├── tools.py                # 工具系统适配
│   ├── events.py               # 事件/Hook 系统
│   └── multiagent.py           # 多智能体编排
├── agents/                      # 现有: 保持不变
│   ├── __init__.py             # 更新: 使用适配层
│   └── types/
├── models.py                    # 更新: 使用适配层
└── ...
```

---

## 🔄 API 映射表

### Agent 创建
```python
# Strands
from strands.agent import Agent
agent = Agent(
    model=model,
    tools=tools,
    system_prompt=prompt,
    callback_handler=handler,
    conversation_manager=conv_mgr,
    hooks=[hook1, hook2]
)

# LangChain
from langchain.agents import create_react_agent
from langchain_core.tools import Tool
agent = create_react_agent(
    llm=llm,
    tools=tools,
    system_prompt=prompt,
    # 需要自实现: callback_handler, hooks
)
```

### 模型
```python
# Strands
from strands.models.openai import OpenAIModel
model = OpenAIModel(model_id="gpt-4", params={...})

# LangChain
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4", ...)
```

### 工具
```python
# Strands
from strands.tools import tool
@tool
def my_tool(x: int) -> int:
    return x * 2

# LangChain
from langchain_core.tools import tool
@tool
def my_tool(x: int) -> int:
    return x * 2
```

### 多智能体
```python
# Strands
from strands.multiagent import Swarm
swarm = Swarm(agents=[agent1, agent2])

# LangChain (使用 LangGraph)
from langgraph.graph import StateGraph
graph = StateGraph(...)
```

---

## 📝 详细任务清单

### Phase 1: 准备工作

#### Task 1.1: 依赖管理
- [ ] 添加 LangChain 依赖到 pyproject.toml
  ```
  langchain>=0.1.0
  langchain-openai>=0.1.0
  langchain-community>=0.1.0
  langgraph>=0.1.0
  ```
- [ ] 创建 requirements-langchain.txt
- [ ] 设置特性开关 (LANGCHAIN_ENABLED)

#### Task 1.2: 测试框架
- [ ] 创建 tests/adapters/ 目录
- [ ] 编写适配层单元测试模板
- [ ] 设置 CI/CD 配置

#### Task 1.3: 文档
- [ ] 创建 API 映射文档
- [ ] 编写迁移指南
- [ ] 记录已知差异

### Phase 2: 核心适配层

#### Task 2.1: 模型适配 (~150 行)
- [ ] 创建 `adapters/models.py`
- [ ] 实现 OpenAI 适配
- [ ] 实现 Ollama 适配
- [ ] 实现 LiteLLM 适配
- [ ] 编写单元测试

#### Task 2.2: 工具适配 (~200 行)
- [ ] 创建 `adapters/tools.py`
- [ ] 实现工具转换逻辑
- [ ] 处理 MCP 工具
- [ ] 编写集成测试

#### Task 2.3: 事件系统 (~300 行)
- [ ] 创建 `adapters/events.py`
- [ ] 实现事件基类
- [ ] 实现 Hook 替代方案
- [ ] 实现流式处理

### Phase 3: Agent 系统

#### Task 3.1: Agent 创建 (~400 行)
- [ ] 创建 `adapters/agents.py`
- [ ] 实现基础 Agent 包装
- [ ] 迁移 9 个智能体工厂
- [ ] 处理参数映射
- [ ] 编写测试

#### Task 3.2: 对话管理 (~150 行)
- [ ] 实现对话历史管理
- [ ] 实现滑动窗口逻辑
- [ ] 集成消息存储

### Phase 4: 多智能体

#### Task 4.1: 多智能体编排 (~200 行) ⭐ 简化
- [ ] 创建 `adapters/multiagent.py`
- [ ] 使用 LangGraph Swarm (直接替代)
- [ ] 创建 Swarm 适配器
- [ ] 编写测试

**注**: LangGraph Swarm 可以直接替代 Strands Swarm，无需自实现编排逻辑

#### Task 4.2: 任务监控 (~300 行)
- [ ] 实现任务追踪
- [ ] 实现步骤监控
- [ ] 集成事件系统

### Phase 5: 集成和测试

#### Task 5.1: 集成测试 (~500 行)
- [ ] 端到端测试
- [ ] 性能基准测试
- [ ] 兼容性测试

#### Task 5.2: 文档更新
- [ ] 更新 README
- [ ] 更新 DESIGN.md
- [ ] 更新 DEPENDENCIES.md
- [ ] 创建迁移指南

---

## 🎯 关键实现细节

### 1. 事件系统实现
```python
# adapters/events.py
class LangChainEventBus:
    def __init__(self):
        self.listeners = {}
    
    def on(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def emit(self, event_type, data):
        for callback in self.listeners.get(event_type, []):
            callback(data)
```

### 2. Agent 包装器
```python
# adapters/agents.py
class LangChainAgent:
    def __init__(self, llm, tools, system_prompt):
        self.agent = create_react_agent(llm, tools, system_prompt)
        self.event_bus = LangChainEventBus()
    
    async def invoke_async(self, query):
        # 实现异步调用
        # 发出事件
        # 返回结果
        pass
```

### 3. 多智能体编排
```python
# adapters/multiagent.py
class LangChainSwarm:
    def __init__(self, agents):
        self.agents = agents
        self.graph = self._build_graph()
    
    def _build_graph(self):
        # 使用 LangGraph 构建状态机
        pass
```

---

## ✅ 验收标准

### 功能完整性
- [ ] 所有 9 个智能体工厂函数正常工作
- [ ] 多智能体编排功能完整
- [ ] 工具系统完全兼容
- [ ] 事件系统功能等价

### 性能
- [ ] 响应时间 ±10% (vs Strands)
- [ ] 内存使用 ±15% (vs Strands)
- [ ] 吞吐量 ±10% (vs Strands)

### 测试覆盖
- [ ] 单元测试覆盖 >80%
- [ ] 集成测试覆盖 >70%
- [ ] 所有关键路径测试通过

### 文档
- [ ] API 文档完整
- [ ] 迁移指南清晰
- [ ] 示例代码可运行

---

## 🚨 回滚计划

1. 保留 Strands 依赖 (可选)
2. 使用特性开关控制
3. 保留原始代码分支
4. 完整的测试覆盖



# Strands ↔ LangChain API 映射参考

---

## 📦 包级别映射

| Strands | LangChain | 说明 |
|---------|-----------|------|
| `strands.agent.Agent` | `langchain.agents.AgentExecutor` | 主要 Agent 类 |
| `strands.multiagent.Swarm` | `langgraph.graph.StateGraph` | 多智能体编排 |
| `strands.models.Model` | `langchain_core.language_models.LLM` | 基础模型接口 |
| `strands.types.tools.AgentTool` | `langchain_core.tools.Tool` | 工具定义 |
| `strands.hooks.HookRegistry` | 自实现 | 事件系统 |

---

## 🤖 Agent 类映射

### 创建
```python
# Strands
agent = Agent(
    model=model,
    tools=tools,
    system_prompt="You are...",
    name="MyAgent",
    agent_id="agent-1",
    callback_handler=handler,
    conversation_manager=conv_mgr,
    hooks=[hook1, hook2]
)

# LangChain
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor

agent = create_react_agent(
    llm=model,
    tools=tools,
    system_prompt="You are..."
)
executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    # 需要自实现: callback_handler, hooks
)
```

### 方法映射

| Strands | LangChain | 说明 |
|---------|-----------|------|
| `agent.invoke(query)` | `executor.invoke({"input": query})` | 同步调用 |
| `agent.invoke_async(query)` | `executor.ainvoke({"input": query})` | 异步调用 |
| `agent.structured_output_async(schema, prompt)` | 需要自实现 | 结构化输出 |
| `agent.stream(query)` | `executor.stream({"input": query})` | 流式输出 |

---

## 🛠️ 工具系统映射

### 工具定义
```python
# Strands
from strands.tools import tool

@tool
def calculator(expression: str) -> float:
    """Calculate mathematical expression"""
    return eval(expression)

# LangChain
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> float:
    """Calculate mathematical expression"""
    return eval(expression)
```

### 工具列表
```python
# Strands
tools = [tool1, tool2, tool3]
agent = Agent(tools=tools, ...)

# LangChain
tools = [tool1, tool2, tool3]
agent = create_react_agent(llm, tools)
```

---

## 🧠 模型映射

### OpenAI
```python
# Strands
from strands.models.openai import OpenAIModel
model = OpenAIModel(
    model_id="gpt-4",
    client_args={"api_key": "..."},
    params={"temperature": 0.5}
)

# LangChain
from langchain_openai import ChatOpenAI
model = ChatOpenAI(
    model="gpt-4",
    api_key="...",
    temperature=0.5
)
```

### Ollama
```python
# Strands
from strands.models.ollama import OllamaModel
model = OllamaModel(
    base_url="http://localhost:8000",
    model_id="llama2",
    temperature=0.5
)

# LangChain
from langchain_community.llms import Ollama
model = Ollama(
    base_url="http://localhost:8000",
    model="llama2",
    temperature=0.5
)
```

### LiteLLM
```python
# Strands
from strands.models.litellm import LiteLLMModel
model = LiteLLMModel(
    model_id="gpt-4",
    params={"api_key": "...", "temperature": 0.5}
)

# LangChain
from langchain_community.llms import LiteLLM
model = LiteLLM(
    model="gpt-4",
    api_key="...",
    temperature=0.5
)
```

---

## 📨 消息类型映射

| Strands | LangChain | 说明 |
|---------|-----------|------|
| `Message` | `BaseMessage` | 基础消息 |
| `ToolUse` | `ToolCall` | 工具调用 |
| `ToolResult` | `ToolMessage` | 工具结果 |
| `StreamEvent` | `StreamEvent` | 流事件 |

### 消息转换
```python
# Strands Message
from strands.types.content import Message
msg = Message(role="user", content="Hello")

# LangChain BaseMessage
from langchain_core.messages import HumanMessage
msg = HumanMessage(content="Hello")
```

---

## 🔗 多智能体映射

### Swarm
```python
# Strands
from strands.multiagent import Swarm
swarm = Swarm(agents=[agent1, agent2, agent3])
result = await swarm.invoke_async(query)

# LangChain (LangGraph)
from langgraph.graph import StateGraph
from langgraph.graph import END

graph = StateGraph(AgentState)
graph.add_node("agent1", agent1_node)
graph.add_node("agent2", agent2_node)
graph.add_edge("agent1", "agent2")
graph.add_edge("agent2", END)
app = graph.compile()
result = await app.ainvoke({"input": query})
```

---

## 🎣 Hook/事件系统映射

### Hook 注册
```python
# Strands
from strands.hooks import HookRegistry
hooks = HookRegistry()
hooks.register(BeforeInvocationEvent, callback)

# LangChain (自实现)
event_bus = EventBus()
event_bus.on("before_invocation", callback)
```

### 事件类型映射

| Strands | LangChain 替代 |
|---------|---------------|
| `BeforeInvocationEvent` | `before_invocation` |
| `AfterInvocationEvent` | `after_invocation` |
| `MessageAddedEvent` | `message_added` |
| `AgentInitializedEvent` | `agent_initialized` |

---

## 💾 对话管理映射

### 对话历史
```python
# Strands
from strands.agent import SlidingWindowConversationManager
conv_mgr = SlidingWindowConversationManager(max_tokens=2000)
agent = Agent(conversation_manager=conv_mgr, ...)

# LangChain
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(max_token_limit=2000)
# 集成到 AgentExecutor
```

---

## 🔄 回调处理映射

### 回调处理器
```python
# Strands
class MyCallbackHandler:
    def __call__(self, **kwargs):
        if "event" in kwargs:
            # 处理流事件
        if "message" in kwargs:
            # 处理消息事件

agent = Agent(callback_handler=MyCallbackHandler(), ...)

# LangChain
from langchain_core.callbacks import BaseCallbackHandler

class MyCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        pass
    def on_llm_end(self, response, **kwargs):
        pass

executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    callbacks=[MyCallbackHandler()]
)
```

---

## 📊 类型系统映射

| Strands | LangChain |
|---------|-----------|
| `AgentResult` | `dict` 或 `AgentAction` |
| `Status` enum | 自定义 enum |
| `StreamEvent` | `StreamEvent` |



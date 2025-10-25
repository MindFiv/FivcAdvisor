# Strands 完全移除计划

## 📊 现状分析

### 所有 Strands 导入位置 (26 处)

#### 类型系统 (5 处)
1. `src/fivcadvisor/agents/types/base.py:58` - `from strands.types.content import Message`
2. `src/fivcadvisor/tasks/types/base.py:21` - `from strands.types.content import Message`
3. `src/fivcadvisor/tasks/types/base.py:22` - `from strands.multiagent.base import Status as TaskStatus`
4. `src/fivcadvisor/app/components/chat_message.py:4` - `from strands.types.content import Message`
5. `src/fivcadvisor/app/views/chats.py:23` - `from strands.types.content import Message, ContentBlock`

#### Agent 和 Swarm (2 处)
6. `src/fivcadvisor/agents/__init__.py:19` - `from strands.agent import Agent`
7. `src/fivcadvisor/agents/__init__.py:20` - `from strands.multiagent import Swarm`

#### Agent 类型和监控 (5 处)
8. `src/fivcadvisor/agents/types/monitors.py:33` - `from strands import Agent`
9. `src/fivcadvisor/agents/types/monitors.py:34` - `from strands.agent import AgentResult, SlidingWindowConversationManager`
10. `src/fivcadvisor/agents/types/monitors.py:35` - `from strands.types.content import Message`
11. `src/fivcadvisor/agents/types/monitors.py:36` - `from strands.types.streaming import StreamEvent`
12. `src/fivcadvisor/agents/types/monitors.py:37` - `from strands.types.tools import ToolUse, ToolResult`

#### Agent 检索器 (2 处)
13. `src/fivcadvisor/agents/types/retrievers.py:3` - `from strands.agent import Agent`
14. `src/fivcadvisor/agents/types/retrievers.py:4` - `from strands.multiagent import MultiAgentBase`

#### 工具系统 (4 处)
15. `src/fivcadvisor/tools/types/configs.py:6` - `from strands.tools.mcp import MCPClient`
16. `src/fivcadvisor/tools/types/bundles.py:11` - `from strands.types.tools import AgentTool`
17. `src/fivcadvisor/tools/types/retrievers.py:4` - `from strands.types.tools import AgentTool`
18. `src/fivcadvisor/tools/types/retrievers.py:5` - `from strands.tools import tool as make_tool`

#### 工具初始化 (3 处)
19. `src/fivcadvisor/tools/__init__.py:15` - `from strands.types.exceptions import MCPClientInitializationError`
20. `src/fivcadvisor/tools/__init__.py:29` - `from strands.tools.registry import ToolRegistry`
21. `src/fivcadvisor/tools/__init__.py:30` - `from strands_tools import (...)`

#### Task 监控 (3 处)
22. `src/fivcadvisor/tasks/types/monitors.py:25` - `from strands import Agent`
23. `src/fivcadvisor/tasks/types/monitors.py:26-33` - `from strands.hooks import (...)`
24. `src/fivcadvisor/tasks/types/monitors.py:34` - `from strands.multiagent import MultiAgentBase`

#### 适配器 (2 处)
25. `src/fivcadvisor/adapters/agents.py:25` - `from strands.types.content import Message, ContentBlock`
26. `src/fivcadvisor/app/utils/chats.py:39` - `from strands.agent import AgentResult`

---

## 🎯 分阶段迁移计划

### 第1阶段: 替换类型系统 (优先级: 高)

**目标**: 替换所有 `strands.types.*` 导入

**替换方案**:
- `Message` → `langchain_core.messages.BaseMessage` 或自定义 `Message` 类
- `ContentBlock` → 自定义或使用 LangChain 的消息内容
- `ToolUse` → `ToolCall` (LangChain)
- `ToolResult` → `ToolMessage` (LangChain)
- `StreamEvent` → 自定义事件类或 LangChain 的流事件

**受影响文件** (5 个):
- `src/fivcadvisor/agents/types/base.py`
- `src/fivcadvisor/tasks/types/base.py`
- `src/fivcadvisor/app/components/chat_message.py`
- `src/fivcadvisor/app/views/chats.py`
- `src/fivcadvisor/adapters/agents.py`

### 第2阶段: 替换工具系统 (优先级: 高)

**目标**: 替换所有 `strands.tools.*` 导入

**替换方案**:
- `AgentTool` → `langchain_core.tools.Tool` 或自定义包装
- `tool` decorator → `langchain_core.tools.tool`
- `MCPClient` → 自定义 MCP 客户端或 LangChain 集成
- `ToolRegistry` → 自定义注册表

**受影响文件** (4 个):
- `src/fivcadvisor/tools/types/configs.py`
- `src/fivcadvisor/tools/types/bundles.py`
- `src/fivcadvisor/tools/types/retrievers.py`
- `src/fivcadvisor/tools/__init__.py`

### 第3阶段: 替换 Agent 和 Swarm (优先级: 中)

**目标**: 移除 `strands.agent.Agent` 和 `strands.multiagent.Swarm` 导入

**现状**: 已有 LangChain 适配器
- `LangChainAgentAdapter` 替代 `Agent`
- `LangGraphSwarmAdapter` 替代 `Swarm`

**受影响文件** (4 个):
- `src/fivcadvisor/agents/__init__.py`
- `src/fivcadvisor/agents/types/monitors.py`
- `src/fivcadvisor/agents/types/retrievers.py`
- `src/fivcadvisor/tasks/types/monitors.py`

### 第4阶段: 替换 Hook 系统 (优先级: 中)

**目标**: 替换 `strands.hooks.*` 导入

**替换方案**:
- 实现自定义事件系统或使用 LangChain 的回调机制
- 保持现有的 `TaskMonitor` 接口

**受影响文件** (1 个):
- `src/fivcadvisor/tasks/types/monitors.py`

### 第5阶段: 清理和测试 (优先级: 高)

**目标**: 移除 strands 依赖，运行所有测试

**步骤**:
1. 从 `pyproject.toml` 移除 `strands` 依赖
2. 运行所有单元测试
3. 运行集成测试
4. 验证 Web 界面功能

---

## 📋 依赖关系

```
第1阶段 (类型系统)
    ↓
第2阶段 (工具系统)
    ↓
第3阶段 (Agent/Swarm)
    ↓
第4阶段 (Hook 系统)
    ↓
第5阶段 (清理和测试)
```

---

## ⚠️ 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|--------|
| 类型不兼容 | 高 | 创建兼容层或使用 Union 类型 |
| Hook 系统缺失 | 中 | 实现自定义事件系统 |
| 工具系统变化 | 中 | 创建适配器层 |
| 测试失败 | 高 | 逐步迁移，频繁测试 |

---

## ✅ 验收标准

- [ ] 所有 strands 导入已移除
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] Web 界面功能正常
- [ ] 没有运行时错误
- [ ] 代码覆盖率 ≥ 80%


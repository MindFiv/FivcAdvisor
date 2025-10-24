# Strands → LangChain 迁移评估报告

**评估日期**: 2025-10-24  
**项目**: FivcAdvisor  
**当前框架**: Strands Agents (v1.9.1+)  
**目标框架**: LangChain

---

## 📊 执行摘要

**可行性**: ✅ **高度可行** (80-85%)  
**难度等级**: 🟠 **中等偏高** (6/10)  
**预计工作量**: 4-6 周（全职开发）  
**风险等级**: 🟡 **中等** (需要充分测试)

---

## 🔍 当前 Strands 依赖分析

### 核心依赖包
```
strands-agents>=1.9.1      # 主框架
strands-agents-tools>=0.2.8 # 工具库和 MCP 集成
```

### 主要使用点 (按重要性排序)

| 模块 | 使用频率 | 复杂度 | 迁移难度 |
|------|--------|-------|--------|
| `Agent` 类 | 极高 | 高 | 🟠 中 |
| `Swarm` (多智能体) | 高 | 高 | 🔴 高 |
| 模型适配器 | 高 | 中 | 🟢 低 |
| 工具系统 | 高 | 中 | 🟠 中 |
| Hook 系统 | 中 | 中 | 🟠 中 |
| 消息类型 | 中 | 低 | 🟢 低 |

### 详细依赖清单

#### 1. **Agent 类** (src/fivcadvisor/agents/__init__.py)
- `from strands.agent import Agent`
- 用途: 创建 9 种专门化智能体
- 关键方法: `invoke_async()`, `structured_output_async()`
- 参数: model, tools, system_prompt, callback_handler, conversation_manager, hooks

#### 2. **多智能体系统** (src/fivcadvisor/agents/__init__.py)
- `from strands.multiagent import Swarm`
- 用途: 创建智能体团队执行复杂任务
- 关键方法: `invoke_async()`

#### 3. **模型适配器** (src/fivcadvisor/models.py)
- `from strands.models import Model`
- `from strands.models.openai import OpenAIModel`
- `from strands.models.ollama import OllamaModel`
- `from strands.models.litellm import LiteLLMModel`
- 用途: 支持多个 LLM 提供商

#### 4. **工具系统** (src/fivcadvisor/tools/)
- `from strands.types.tools import AgentTool`
- `from strands.tools import tool as make_tool`
- 用途: 定义和管理工具

#### 5. **Hook 系统** (src/fivcadvisor/tasks/types/monitors.py)
- `from strands.hooks import HookRegistry, HookEvent, BeforeInvocationEvent, AfterInvocationEvent, MessageAddedEvent`
- 用途: 监控任务执行生命周期

#### 6. **类型系统** (多个文件)
- `from strands.types.content import Message`
- `from strands.types.streaming import StreamEvent`
- `from strands.types.tools import ToolUse, ToolResult`
- `from strands.agent import AgentResult, SlidingWindowConversationManager`
- `from strands.multiagent.base import Status as TaskStatus`

---

## 🎯 LangChain 对标分析

### 优势
✅ 更成熟的生态系统  
✅ 更好的文档和社区支持  
✅ 更灵活的工具集成  
✅ 更好的流式处理支持  
✅ 更多的第三方集成  

### 劣势
❌ 多智能体编排不如 Strands 原生  
❌ 需要自己实现 Hook 系统  
❌ 工具定义方式不同  
❌ 消息格式差异  

---

## 📋 迁移范围

### 需要重写的模块 (按优先级)

1. **Agent 创建系统** (~500 行)
   - 9 个智能体工厂函数
   - 参数映射和验证

2. **多智能体编排** (~300 行)
   - Swarm 替代方案
   - 团队协调逻辑

3. **模型适配层** (~150 行)
   - LangChain ChatModel 包装
   - 提供商适配

4. **监控系统** (~400 行)
   - Hook 系统替代
   - 事件追踪

5. **工具系统** (~200 行)
   - 工具定义转换
   - MCP 集成适配

### 可保留的模块

✅ 数据模型 (Pydantic models)  
✅ 存储库模式  
✅ 业务逻辑  
✅ UI 层  
✅ 配置系统  

---

## 🔧 技术迁移方案

### 方案 A: 完全迁移 (推荐)
**优点**: 完全利用 LangChain 生态  
**缺点**: 工作量最大  
**时间**: 5-6 周

### 方案 B: 适配层方案
**优点**: 最小化改动  
**缺点**: 维护两套系统  
**时间**: 3-4 周

### 方案 C: 渐进式迁移
**优点**: 风险最低  
**缺点**: 过渡期长  
**时间**: 6-8 周

---

## ⚠️ 关键风险

| 风险 | 影响 | 缓解策略 |
|------|------|--------|
| 多智能体编排 | 高 | 使用 LangGraph 或自实现 |
| Hook 系统 | 中 | 实现自定义事件系统 |
| 工具兼容性 | 中 | 创建工具适配层 |
| 流式处理 | 中 | 使用 LangChain 流式 API |
| 测试覆盖 | 高 | 完整的集成测试 |

---

## 📅 实施规划

### 第 1 阶段: 准备 (1 周)
- [ ] 创建 LangChain 适配层框架
- [ ] 建立测试基础设施
- [ ] 文档化 API 映射

### 第 2 阶段: 核心迁移 (2 周)
- [ ] 迁移模型适配层
- [ ] 迁移 Agent 创建系统
- [ ] 迁移工具系统

### 第 3 阶段: 高级功能 (1.5 周)
- [ ] 实现多智能体编排
- [ ] 实现监控系统
- [ ] 实现 Hook 替代方案

### 第 4 阶段: 测试和优化 (1.5 周)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能测试
- [ ] 文档更新

---

## 🚀 建议

**立即行动**:
1. 创建 `langchain-adapter` 分支
2. 建立 LangChain 依赖
3. 实现模型适配层作为 PoC

**关键决策**:
- 选择多智能体方案 (LangGraph vs 自实现)
- 决定是否保留 Strands 作为备选

**后续步骤**:
- 详细的 API 映射文档
- 逐个模块的迁移计划
- 完整的测试策略



# Adapters 移除执行清单

## 📋 第1阶段: 代码重构

### 1.1 Models 模块重构

#### 步骤 1: 分析现有代码
- [ ] 查看 `src/fivcadvisor/adapters/models.py` 的所有函数
- [ ] 查看 `src/fivcadvisor/models.py` 的现有结构
- [ ] 确认依赖关系

#### 步骤 2: 集成模型创建函数
- [ ] 复制 `create_openai_model()` 到 `models.py`
- [ ] 复制 `create_ollama_model()` 到 `models.py`
- [ ] 复制 `create_litellm_model()` 到 `models.py`
- [ ] 复制 `create_langchain_model()` 到 `models.py`
- [ ] 复制 `create_default_langchain_model()` 到 `models.py`
- [ ] 复制 `create_chat_langchain_model()` 到 `models.py`
- [ ] 复制 `create_reasoning_langchain_model()` 到 `models.py`
- [ ] 复制 `create_coding_langchain_model()` 到 `models.py`

#### 步骤 3: 更新导入
- [ ] 移除 `from .adapters import create_*_model` 的导入
- [ ] 更新 `__all__` 导出列表

#### 步骤 4: 验证
- [ ] 运行 `pytest tests/test_langchain_models_adapter.py -v`
- [ ] 检查 `src/fivcadvisor/models.py` 中没有 adapters 导入

---

### 1.2 Agents 模块重构

#### 步骤 1: 创建新的 Agent 类文件
- [ ] 创建 `src/fivcadvisor/agents/types/langchain_adapter.py`
- [ ] 复制 `LangChainAgentAdapter` 类到新文件
- [ ] 复制 `create_langchain_agent()` 函数到新文件

#### 步骤 2: 更新导入
- [ ] 在 `src/fivcadvisor/agents/__init__.py` 中导入新位置
- [ ] 移除 `from fivcadvisor.adapters import LangChainAgentAdapter, create_langchain_agent`

#### 步骤 3: 验证
- [ ] 运行 `pytest tests/test_langchain_agents_adapter.py -v`
- [ ] 运行 `pytest tests/test_agent_creator.py -v`
- [ ] 检查没有 adapters 导入

---

### 1.3 Multiagent 模块重构

#### 步骤 1: 创建新的 Swarm 类文件
- [ ] 创建 `src/fivcadvisor/agents/types/swarm.py`
- [ ] 复制 `LangGraphSwarmAdapter` 类到新文件
- [ ] 复制 `create_langchain_swarm()` 函数到新文件
- [ ] 复制 `SwarmState` TypedDict 到新文件

#### 步骤 2: 更新导入
- [ ] 在 `src/fivcadvisor/agents/__init__.py` 中导入新位置
- [ ] 移除 `from fivcadvisor.adapters import LangGraphSwarmAdapter, create_langchain_swarm`

#### 步骤 3: 验证
- [ ] 运行 `pytest tests/test_langgraph_swarm_adapter.py -v`
- [ ] 运行 `python examples/swarm_example.py`
- [ ] 检查没有 adapters 导入

---

### 1.4 Tools 模块重构

#### 步骤 1: 集成工具转换函数
- [ ] 复制 `convert_strands_tool_to_langchain()` 到 `src/fivcadvisor/tools/`
- [ ] 复制 `convert_strands_tools_to_langchain()` 到 `src/fivcadvisor/tools/`
- [ ] 复制 `is_strands_tool()` 到 `src/fivcadvisor/tools/`
- [ ] 复制 `is_langchain_tool()` 到 `src/fivcadvisor/tools/`
- [ ] 复制 `ToolAdapter` 类到 `src/fivcadvisor/tools/`
- [ ] 复制 `adapt_tool()` 和 `adapt_tools()` 到 `src/fivcadvisor/tools/`

#### 步骤 2: 更新导入
- [ ] 更新所有导入路径
- [ ] 更新 `__all__` 导出列表

#### 步骤 3: 验证
- [ ] 运行 `pytest tests/test_langchain_tools_events_adapter.py::TestToolsAdapter -v`
- [ ] 检查没有 adapters 导入

---

### 1.5 Events 模块重构

#### 步骤 1: 集成事件系统
- [ ] 复制 `EventType` enum 到 `src/fivcadvisor/events/`
- [ ] 复制所有 Event 类到 `src/fivcadvisor/events/`
- [ ] 复制 `EventBus` 类到 `src/fivcadvisor/events/`
- [ ] 复制 `get_event_bus()`, `emit_event()`, `subscribe_to_event()` 到 `src/fivcadvisor/events/`

#### 步骤 2: 更新导入
- [ ] 更新所有导入路径
- [ ] 更新 `__all__` 导出列表

#### 步骤 3: 验证
- [ ] 运行 `pytest tests/test_langchain_tools_events_adapter.py::TestEventBus -v`
- [ ] 检查没有 adapters 导入

---

## 🗑️ 第2阶段: 清理

### 步骤 1: 删除适配器目录
- [ ] 备份 `src/fivcadvisor/adapters/` (可选)
- [ ] 删除 `src/fivcadvisor/adapters/` 目录

### 步骤 2: 删除适配器测试文件
- [ ] 删除 `tests/test_langchain_agents_adapter.py`
- [ ] 删除 `tests/test_langchain_models_adapter.py`
- [ ] 删除 `tests/test_langchain_tools_events_adapter.py`
- [ ] 删除 `tests/test_langgraph_swarm_adapter.py`

### 步骤 3: 更新文档
- [ ] 更新 `docs/LANGCHAIN_MIGRATION_GUIDE.md` - 移除适配器部分
- [ ] 更新 `docs/LANGCHAIN_API_REFERENCE.md` - 移除适配器 API
- [ ] 更新 `MIGRATION_PROGRESS.md` - 标记适配器移除完成
- [ ] 删除或更新 `docs/LANGGRAPH_SWARM_GUIDE.md` 中的适配器引用

### 步骤 4: 更新示例
- [ ] 更新 `examples/swarm_example.py` 导入路径
- [ ] 更新 `examples/agents/run_agents.py` 导入路径

---

## ✅ 第3阶段: 验证

### 步骤 1: 全局导入检查
- [ ] 运行: `grep -r "from fivcadvisor.adapters" src/`
- [ ] 运行: `grep -r "from fivcadvisor.adapters" tests/`
- [ ] 运行: `grep -r "from fivcadvisor.adapters" examples/`
- [ ] 运行: `grep -r "import fivcadvisor.adapters" src/`
- [ ] 确认没有结果

### 步骤 2: 运行所有测试
- [ ] 运行: `pytest tests/ -v`
- [ ] 确认所有测试通过
- [ ] 检查没有导入错误

### 步骤 3: 功能验证
- [ ] 运行 CLI: `fivcadvisor run Generic --query "test"`
- [ ] 运行 Web UI: `streamlit run src/fivcadvisor/app/__init__.py`
- [ ] 运行示例: `python examples/swarm_example.py`
- [ ] 检查没有导入错误

### 步骤 4: 性能测试
- [ ] 运行: `pytest tests/test_langchain_performance.py -v`
- [ ] 确认性能指标正常

### 步骤 5: 代码质量检查
- [ ] 运行: `ruff check src/`
- [ ] 运行: `ruff format src/`
- [ ] 检查没有 linting 错误

---

## 📊 进度跟踪

| 阶段 | 完成度 | 备注 |
|------|--------|------|
| 1.1 Models 重构 | 0% | 待开始 |
| 1.2 Agents 重构 | 0% | 待开始 |
| 1.3 Multiagent 重构 | 0% | 待开始 |
| 1.4 Tools 重构 | 0% | 待开始 |
| 1.5 Events 重构 | 0% | 待开始 |
| 2 清理 | 0% | 待开始 |
| 3 验证 | 0% | 待开始 |

---

## 🔗 相关文件

- 主计划: `ADAPTERS_REMOVAL_PLAN.md`
- 分析报告: 见下方

### 受影响的文件列表

**源代码**:
- `src/fivcadvisor/adapters/__init__.py`
- `src/fivcadvisor/adapters/agents.py`
- `src/fivcadvisor/adapters/models.py`
- `src/fivcadvisor/adapters/tools.py`
- `src/fivcadvisor/adapters/events.py`
- `src/fivcadvisor/adapters/multiagent.py`

**导入文件**:
- `src/fivcadvisor/agents/__init__.py`
- `src/fivcadvisor/models.py`

**测试文件**:
- `tests/test_langchain_agents_adapter.py`
- `tests/test_langchain_models_adapter.py`
- `tests/test_langchain_tools_events_adapter.py`
- `tests/test_langgraph_swarm_adapter.py`

**示例文件**:
- `examples/swarm_example.py`
- `examples/agents/run_agents.py`

**文档文件**:
- `docs/LANGCHAIN_MIGRATION_GUIDE.md`
- `docs/LANGCHAIN_API_REFERENCE.md`
- `docs/LANGGRAPH_SWARM_GUIDE.md`
- `MIGRATION_PROGRESS.md`


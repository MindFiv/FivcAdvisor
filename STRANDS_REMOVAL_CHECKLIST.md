# Strands 移除 - 执行清单

## 📋 准备阶段

- [ ] 阅读 `STRANDS_REMOVAL_SUMMARY.md`
- [ ] 阅读 `STRANDS_REMOVAL_PLAN.md`
- [ ] 阅读 `STRANDS_REMOVAL_IMPLEMENTATION.md`
- [ ] 阅读 `STRANDS_REMOVAL_FILE_MAPPING.md`
- [ ] 创建新分支: `git checkout -b feature/remove-strands`
- [ ] 确保所有测试通过: `pytest tests/ -v`

---

## 🔧 第1阶段: 替换类型系统 (1-2 天)

### 1.1 创建兼容层

- [ ] 创建 `src/fivcadvisor/types/__init__.py`
- [ ] 创建 `src/fivcadvisor/types/compat.py`
- [ ] 定义 `Message` 类型
- [ ] 定义 `ContentBlock` 类型
- [ ] 定义 `ToolUse` 类型
- [ ] 定义 `ToolResult` 类型
- [ ] 定义 `StreamEvent` 类
- [ ] 运行类型检查: `mypy src/fivcadvisor/types/`

### 1.2 更新 `src/fivcadvisor/agents/types/base.py`

- [ ] 替换 Message 导入
- [ ] 定义本地 TaskStatus enum
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_agents_runtime.py -v`

### 1.3 更新 `src/fivcadvisor/tasks/types/base.py`

- [ ] 替换 Message 导入
- [ ] 替换 TaskStatus 导入
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_task_monitor.py -v`

### 1.4 更新 `src/fivcadvisor/app/components/chat_message.py`

- [ ] 替换 Message 导入
- [ ] 验证类型检查通过
- [ ] 运行相关测试

### 1.5 更新 `src/fivcadvisor/app/views/chats.py`

- [ ] 替换 Message 和 ContentBlock 导入
- [ ] 验证类型检查通过
- [ ] 运行相关测试

### 1.6 更新 `src/fivcadvisor/adapters/agents.py`

- [ ] 替换 Message 和 ContentBlock 导入
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_langchain_agents_adapter.py -v`

### 1.7 第1阶段验证

- [ ] 所有类型检查通过
- [ ] 所有相关测试通过
- [ ] 没有导入错误
- [ ] 提交: `git commit -m "Phase 1: Replace type system"`

---

## 🔧 第2阶段: 替换工具系统 (1-2 天)

### 2.1 创建工具兼容层

- [ ] 创建 `src/fivcadvisor/tools/compat.py`
- [ ] 定义 `AgentTool` 类型
- [ ] 定义 `MCPClientInitializationError` 异常
- [ ] 导出 `tool` 装饰器
- [ ] 运行类型检查

### 2.2 更新 `src/fivcadvisor/tools/types/bundles.py`

- [ ] 替换 AgentTool 导入
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_tools_bundle.py -v`

### 2.3 更新 `src/fivcadvisor/tools/types/retrievers.py`

- [ ] 替换 AgentTool 导入
- [ ] 替换 tool 装饰器导入
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_tools_retriever.py -v`

### 2.4 更新 `src/fivcadvisor/tools/types/configs.py`

- [ ] 处理 MCPClient 导入
- [ ] 选项 A: 使用 mcp 库直接
- [ ] 选项 B: 创建自定义包装
- [ ] 验证 MCP 客户端工作
- [ ] 运行相关测试

### 2.5 更新 `src/fivcadvisor/tools/__init__.py`

- [ ] 替换 MCPClientInitializationError 导入
- [ ] 处理 ToolRegistry 导入
- [ ] 处理 strands_tools 导入
- [ ] 验证工具加载正常
- [ ] 运行相关测试: `pytest tests/test_tools_config.py -v`

### 2.6 第2阶段验证

- [ ] 所有类型检查通过
- [ ] 所有工具测试通过
- [ ] 工具加载正常
- [ ] MCP 客户端工作
- [ ] 提交: `git commit -m "Phase 2: Replace tool system"`

---

## 🔧 第3阶段: 替换 Agent/Swarm (1 天)

### 3.1 更新 `src/fivcadvisor/agents/__init__.py`

- [ ] 移除 `from strands.agent import Agent`
- [ ] 移除 `from strands.multiagent import Swarm`
- [ ] 更新 `create_default_agent()` 返回类型
- [ ] 更新 `create_generic_agent_swarm()` 返回类型
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_agent_creator.py -v`

### 3.2 更新 `src/fivcadvisor/agents/types/monitors.py`

- [ ] 移除 `from strands import Agent`
- [ ] 替换 AgentResult 和 SlidingWindowConversationManager
- [ ] 替换 Message 导入
- [ ] 替换 StreamEvent 导入
- [ ] 替换 ToolUse 和 ToolResult 导入
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_agent_monitor.py -v`

### 3.3 更新 `src/fivcadvisor/agents/types/retrievers.py`

- [ ] 移除 `from strands.agent import Agent`
- [ ] 移除 `from strands.multiagent import MultiAgentBase`
- [ ] 更新 `AgentsCreatorBase` 返回类型
- [ ] 验证类型检查通过
- [ ] 运行相关测试

### 3.4 更新 `src/fivcadvisor/tasks/types/monitors.py`

- [ ] 移除 `from strands import Agent`
- [ ] 移除 `from strands.multiagent import MultiAgentBase`
- [ ] 保留 Hook 导入 (第4阶段处理)
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_task_monitor.py -v`

### 3.5 第3阶段验证

- [ ] 所有类型检查通过
- [ ] 所有 Agent 测试通过
- [ ] Agent 创建和执行正常
- [ ] 提交: `git commit -m "Phase 3: Replace Agent and Swarm"`

---

## 🔧 第4阶段: 替换 Hook 系统 (1 天)

### 4.1 创建事件系统

- [ ] 创建 `src/fivcadvisor/events/__init__.py`
- [ ] 创建 `src/fivcadvisor/events/hooks.py`
- [ ] 定义 `HookEvent` 类
- [ ] 定义 `HookRegistry` 类
- [ ] 定义事件类型常量
- [ ] 运行类型检查

### 4.2 更新 `src/fivcadvisor/tasks/types/monitors.py`

- [ ] 替换 Hook 导入
- [ ] 更新 TaskMonitor 使用新事件系统
- [ ] 验证类型检查通过
- [ ] 运行相关测试: `pytest tests/test_task_monitor.py -v`

### 4.3 第4阶段验证

- [ ] 所有类型检查通过
- [ ] 所有 Task 测试通过
- [ ] Hook 事件触发正常
- [ ] 提交: `git commit -m "Phase 4: Replace Hook system"`

---

## 🔧 第5阶段: 清理和测试 (1-2 天)

### 5.1 移除依赖

- [ ] 编辑 `pyproject.toml`
- [ ] 移除 `strands` 依赖
- [ ] 移除 `strands-tools` 依赖
- [ ] 移除 `strands_tools` 依赖
- [ ] 运行 `uv sync` 更新依赖

### 5.2 运行所有测试

- [ ] 运行单元测试: `pytest tests/ -v`
- [ ] 检查测试覆盖率: `pytest tests/ --cov=src/fivcadvisor`
- [ ] 确保覆盖率 ≥ 80%
- [ ] 运行集成测试: `pytest tests/test_*_integration.py -v`

### 5.3 验证功能

- [ ] 启动 Web 界面: `streamlit run src/fivcadvisor/app/main.py`
- [ ] 测试聊天功能
- [ ] 测试任务执行
- [ ] 测试工具调用
- [ ] 检查日志中没有错误

### 5.4 代码质量检查

- [ ] 运行 linting: `pylint src/fivcadvisor`
- [ ] 运行类型检查: `mypy src/fivcadvisor`
- [ ] 运行格式检查: `black --check src/fivcadvisor`
- [ ] 修复任何问题

### 5.5 最终验证

- [ ] 所有测试通过 (82+ 测试)
- [ ] 代码覆盖率 ≥ 80%
- [ ] 没有 linting 错误
- [ ] 类型检查通过
- [ ] Web 界面功能正常
- [ ] 没有运行时错误

### 5.6 完成

- [ ] 提交: `git commit -m "Phase 5: Cleanup and testing"`
- [ ] 创建 PR: `git push origin feature/remove-strands`
- [ ] 请求代码审查
- [ ] 合并到 main 分支

---

## 📊 进度跟踪

| 阶段 | 状态 | 开始日期 | 完成日期 | 备注 |
|------|------|---------|---------|------|
| 准备 | ⬜ | - | - | - |
| 第1阶段 | ⬜ | - | - | - |
| 第2阶段 | ⬜ | - | - | - |
| 第3阶段 | ⬜ | - | - | - |
| 第4阶段 | ⬜ | - | - | - |
| 第5阶段 | ⬜ | - | - | - |

---

## 🆘 故障排除

### 问题: 导入错误
**解决**: 检查新的导入路径是否正确，运行 `python -c "from fivcadvisor.types.compat import Message"`

### 问题: 类型不匹配
**解决**: 检查类型定义是否与使用位置匹配，运行 `mypy src/fivcadvisor`

### 问题: 测试失败
**解决**: 检查测试是否需要更新以适应新的类型，逐个修复失败的测试

### 问题: 运行时错误
**解决**: 检查日志，确保所有依赖都已正确替换

---

## 📞 联系方式

如有问题，请参考:
- `STRANDS_REMOVAL_PLAN.md` - 详细计划
- `STRANDS_REMOVAL_IMPLEMENTATION.md` - 实施指南
- `STRANDS_REMOVAL_FILE_MAPPING.md` - 文件映射


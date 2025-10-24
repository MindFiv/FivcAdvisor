# 迁移快速开始指南

---

## 🚀 5 分钟快速了解

### 当前状态
- **框架**: Strands Agents v1.9.1+
- **依赖**: strands-agents, strands-agents-tools
- **代码量**: ~2000 行 Strands 相关代码
- **复杂度**: 中等 (9 个智能体 + 多智能体编排)

### 迁移目标
- **框架**: LangChain + LangGraph
- **优势**: 更好的生态、更多集成、更活跃的社区
- **工作量**: 4-6 周
- **风险**: 中等 (需要充分测试)

### 关键决策
1. **多智能体方案**: 使用 LangGraph (官方推荐)
2. **事件系统**: 自实现 EventBus
3. **迁移策略**: 完全迁移 (不保留 Strands)
4. **测试**: 完整的单元 + 集成测试

---

## 📊 影响范围

### 需要改动的文件 (~15 个)
```
src/fivcadvisor/
├── models.py                    # 模型适配
├── agents/__init__.py           # Agent 创建
├── agents/types/monitors.py     # 监控系统
├── agents/types/base.py         # 数据模型 (可能需要调整)
├── tasks/types/monitors.py      # 任务监控
├── tools/types/retrievers.py    # 工具系统
└── adapters/                    # 新增适配层
    ├── __init__.py
    ├── models.py
    ├── agents.py
    ├── tools.py
    ├── events.py
    └── multiagent.py
```

### 可保留的文件 (~30 个)
- 所有 Pydantic 数据模型
- 存储库模式实现
- 业务逻辑
- UI 层
- 配置系统

---

## 🎯 三个关键里程碑

### 里程碑 1: 模型适配 (1 周)
**目标**: 验证 LangChain 模型可用性

```python
# adapters/models.py
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

def create_langchain_model(provider, **kwargs):
    if provider == "openai":
        return ChatOpenAI(model=kwargs["model"], ...)
    elif provider == "ollama":
        return Ollama(model=kwargs["model"], ...)
```

**验收**: 所有 3 个模型提供商正常工作

### 里程碑 2: Agent 系统 (2 周)
**目标**: 迁移 9 个智能体工厂函数

```python
# adapters/agents.py
from langchain.agents import create_react_agent

def create_default_agent(**kwargs):
    llm = create_langchain_model(...)
    tools = kwargs.get("tools", [])
    agent = create_react_agent(llm, tools, ...)
    return AgentExecutor.from_agent_and_tools(...)
```

**验收**: 所有 9 个智能体创建成功

### 里程碑 3: 多智能体 (2 周)
**目标**: 实现 Swarm 替代方案

```python
# adapters/multiagent.py
from langgraph.graph import StateGraph

class LangChainSwarm:
    def __init__(self, agents):
        self.graph = StateGraph(...)
        # 构建状态机
```

**验收**: 团队协调正常工作

---

## 🔧 立即可做的事

### 1. 创建分支
```bash
git checkout -b feature/langchain-migration
```

### 2. 添加依赖
```bash
pip install langchain langchain-openai langchain-community langgraph
```

### 3. 创建适配层框架
```bash
mkdir -p src/fivcadvisor/adapters
touch src/fivcadvisor/adapters/__init__.py
touch src/fivcadvisor/adapters/models.py
touch src/fivcadvisor/adapters/agents.py
touch src/fivcadvisor/adapters/tools.py
touch src/fivcadvisor/adapters/events.py
touch src/fivcadvisor/adapters/multiagent.py
```

### 4. 编写第一个测试
```python
# tests/adapters/test_models.py
import pytest
from fivcadvisor.adapters.models import create_langchain_model

def test_create_openai_model():
    model = create_langchain_model("openai", model="gpt-4")
    assert model is not None
    assert hasattr(model, "invoke")
```

---

## 📈 成功指标

### 功能指标
- ✅ 所有 9 个智能体工作
- ✅ 多智能体编排完整
- ✅ 工具系统兼容
- ✅ 事件系统功能等价

### 质量指标
- ✅ 单元测试覆盖 >80%
- ✅ 集成测试覆盖 >70%
- ✅ 所有关键路径测试通过
- ✅ 无性能回退 (±10%)

### 文档指标
- ✅ API 文档完整
- ✅ 迁移指南清晰
- ✅ 示例代码可运行
- ✅ 已知问题记录

---

## ⚠️ 常见陷阱

### 1. 忽视多智能体复杂性
❌ 错误: 直接用 LangChain Agent 替换 Strands Agent
✅ 正确: 使用 LangGraph 构建状态机

### 2. 跳过测试
❌ 错误: 快速迁移，测试不足
✅ 正确: 每个模块都有完整的测试

### 3. 忽视性能
❌ 错误: 不进行性能基准测试
✅ 正确: 建立基准，监控回退

### 4. 不处理错误情况
❌ 错误: 只测试成功路径
✅ 正确: 测试所有错误情况

### 5. 文档不更新
❌ 错误: 代码改了，文档没改
✅ 正确: 同步更新所有文档

---

## 📞 获取帮助

### 资源
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [API 映射参考](./STRANDS_LANGCHAIN_MAPPING.md)
- [风险分析](./MIGRATION_RISKS.md)

### 关键联系人
- 架构决策: 需要团队讨论
- 技术问题: 查看 LangChain 文档
- 集成问题: 查看 API 映射

---

## 📅 建议时间表

```
Week 1: 准备 + 模型适配
├── Day 1-2: 环境设置、依赖安装
├── Day 3-4: 模型适配层实现
└── Day 5: 模型测试和验证

Week 2-3: Agent 系统
├── Week 2: Agent 创建系统迁移
├── Week 3: 工具系统迁移

Week 4: 多智能体
├── 多智能体编排实现
└── 集成测试

Week 5-6: 测试和优化
├── 完整的集成测试
├── 性能优化
└── 文档更新
```

---

## ✅ 检查清单

### 开始前
- [ ] 阅读所有迁移文档
- [ ] 理解 API 映射
- [ ] 了解风险和缓解策略
- [ ] 获得团队同意

### 进行中
- [ ] 每天更新进度
- [ ] 及时处理阻塞
- [ ] 定期进行代码审查
- [ ] 保持测试覆盖

### 完成后
- [ ] 所有测试通过
- [ ] 文档完整
- [ ] 性能验证
- [ ] 知识转移



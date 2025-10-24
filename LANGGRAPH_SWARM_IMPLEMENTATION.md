# LangGraph Swarm 实施指南

**目标**: 用 LangGraph Swarm 直接替代 Strands Swarm  
**工作量**: 18 小时  
**难度**: 🟢 低

---

## 📋 实施步骤

### Step 1: 安装依赖 (30 分钟)

```bash
# 安装 LangGraph Swarm
pip install langgraph-swarm

# 验证安装
python -c "from langgraph_swarm import create_swarm; print('OK')"
```

更新 `pyproject.toml`:
```toml
[project]
dependencies = [
    # ... 现有依赖 ...
    "langgraph-swarm>=0.1.0",
]
```

---

### Step 2: 创建适配层 (2 小时)

创建 `src/fivcadvisor/adapters/multiagent.py`:

```python
"""LangGraph Swarm 适配层"""

from typing import List, Optional, Any
from langgraph_swarm import create_swarm
from langgraph.graph import StateGraph


class LangGraphSwarmAdapter:
    """LangGraph Swarm 适配器，提供 Strands 兼容 API"""
    
    def __init__(self, agents: List[Any], default_agent_name: Optional[str] = None):
        """
        初始化 Swarm
        
        Args:
            agents: 智能体列表
            default_agent_name: 默认智能体名称
        """
        if not agents:
            raise ValueError("At least one agent required")
        
        self.agents = agents
        self.default_agent_name = default_agent_name or agents[0].name
        
        # 创建 LangGraph Swarm
        self.workflow = create_swarm(
            agents=agents,
            default_active_agent=self.default_agent_name
        )
        self.app = self.workflow.compile()
    
    async def invoke_async(self, query: str, **kwargs) -> dict:
        """
        异步调用 Swarm
        
        Args:
            query: 用户查询
            **kwargs: 其他参数
            
        Returns:
            结果字典
        """
        result = await self.app.ainvoke(
            {"messages": [{"role": "user", "content": query}]},
            config=kwargs.get("config")
        )
        return result
    
    def invoke(self, query: str, **kwargs) -> dict:
        """同步调用 Swarm (如需要)"""
        import asyncio
        return asyncio.run(self.invoke_async(query, **kwargs))


def create_langchain_swarm(
    agents: List[Any],
    default_agent_name: Optional[str] = None,
    **kwargs
) -> LangGraphSwarmAdapter:
    """
    创建 LangGraph Swarm
    
    Args:
        agents: 智能体列表
        default_agent_name: 默认智能体名称
        **kwargs: 其他参数
        
    Returns:
        LangGraphSwarmAdapter 实例
    """
    return LangGraphSwarmAdapter(agents, default_agent_name)
```

---

### Step 3: 更新 Agent 创建 (1 小时)

修改 `src/fivcadvisor/agents/__init__.py`:

```python
# 在文件顶部添加导入
from fivcadvisor.adapters.multiagent import create_langchain_swarm

# 替换 Strands 导入
# from strands.multiagent import Swarm  # 删除这行

# 更新 create_generic_agent_swarm 函数
@agent_creator(name="Generic Swarm")
def create_generic_agent_swarm(
    *args,
    team: Optional[TaskTeam] = None,
    tools_retriever: Optional[tools.ToolsRetriever] = None,
    **kwargs,
):
    """Create a generic swarm of agents."""
    if not team:
        raise RuntimeError("team not provided")

    if not tools_retriever:
        raise RuntimeError("tools_retriever not provided")

    s_agents = []
    for s in team.specialists:
        s_tools = tools_retriever.get_batch(s.tools)
        s_tools = [t for t in s_tools if t is not None]
        s_agents.append(
            create_default_agent(
                name=s.name,
                tools=s_tools,
                system_prompt=s.backstory,
                **kwargs,
            )
        )
    
    # 使用 LangGraph Swarm 替代 Strands Swarm
    return create_langchain_swarm(s_agents)
```

---

### Step 4: 更新调用方式 (1 小时)

#### 在 TaskMonitor 中

修改 `src/fivcadvisor/tasks/types/monitors.py`:

```python
# 旧方式
result = await swarm.invoke_async("Your query")

# 新方式
result = await swarm.invoke_async("Your query")
# 结果格式: {"messages": [...]}
# 提取最后一条消息
if result.get("messages"):
    final_message = result["messages"][-1]
    content = final_message.get("content", "")
```

---

### Step 5: 编写测试 (2 小时)

创建 `tests/adapters/test_multiagent.py`:

```python
"""LangGraph Swarm 适配层测试"""

import pytest
from unittest.mock import Mock, AsyncMock
from fivcadvisor.adapters.multiagent import (
    LangGraphSwarmAdapter,
    create_langchain_swarm
)


class TestLangGraphSwarmAdapter:
    """LangGraph Swarm 适配器测试"""
    
    def test_adapter_creation(self):
        """测试适配器创建"""
        # 创建模拟智能体
        agent1 = Mock()
        agent1.name = "agent1"
        
        adapter = LangGraphSwarmAdapter([agent1])
        assert adapter is not None
        assert adapter.default_agent_name == "agent1"
    
    def test_adapter_requires_agents(self):
        """测试适配器需要智能体"""
        with pytest.raises(ValueError):
            LangGraphSwarmAdapter([])
    
    def test_create_langchain_swarm(self):
        """测试创建 LangGraph Swarm"""
        agent1 = Mock()
        agent1.name = "agent1"
        
        swarm = create_langchain_swarm([agent1])
        assert isinstance(swarm, LangGraphSwarmAdapter)
    
    @pytest.mark.asyncio
    async def test_invoke_async(self):
        """测试异步调用"""
        agent1 = Mock()
        agent1.name = "agent1"
        
        adapter = LangGraphSwarmAdapter([agent1])
        
        # 模拟 app.ainvoke
        adapter.app.ainvoke = AsyncMock(return_value={
            "messages": [
                {"role": "user", "content": "test"},
                {"role": "assistant", "content": "response"}
            ]
        })
        
        result = await adapter.invoke_async("test query")
        assert "messages" in result
        assert len(result["messages"]) == 2


class TestSwarmIntegration:
    """Swarm 集成测试"""
    
    @pytest.mark.asyncio
    async def test_swarm_with_multiple_agents(self):
        """测试多智能体 Swarm"""
        # 这里需要实际的智能体对象
        # 可以使用 create_react_agent 创建
        pass
```

---

### Step 6: 集成测试 (2 小时)

更新 `tests/test_execution_integration.py`:

```python
# 添加 Swarm 测试
@pytest.mark.asyncio
async def test_swarm_creation_with_langgraph():
    """测试 LangGraph Swarm 创建"""
    from fivcadvisor.tasks.types import TaskTeam, TaskRequirement
    from fivcadvisor import agents, tools
    
    # 创建任务团队
    team = TaskTeam(
        specialists=[
            TaskRequirement(
                name="specialist1",
                backstory="You are specialist 1",
                tools=[]
            )
        ]
    )
    
    # 创建 Swarm
    swarm = agents.create_generic_agent_swarm(
        team=team,
        tools_retriever=tools.default_retriever
    )
    
    assert swarm is not None
```

---

### Step 7: 性能测试 (1 小时)

创建 `tests/test_swarm_performance.py`:

```python
"""Swarm 性能测试"""

import pytest
import time
from fivcadvisor.adapters.multiagent import create_langchain_swarm


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_swarm_performance(benchmark):
    """测试 Swarm 性能"""
    # 创建模拟智能体
    from unittest.mock import Mock
    
    agent = Mock()
    agent.name = "test_agent"
    
    swarm = create_langchain_swarm([agent])
    
    # 基准测试
    async def invoke():
        return await swarm.invoke_async("test query")
    
    # 运行基准测试
    # benchmark(invoke)  # 需要同步版本
```

---

## 🔄 迁移检查清单

### 准备
- [ ] 安装 langgraph-swarm
- [ ] 阅读 LangGraph Swarm 文档
- [ ] 创建 feature 分支

### 实施
- [ ] 创建适配层 (adapters/multiagent.py)
- [ ] 更新 Agent 创建 (agents/__init__.py)
- [ ] 更新调用方式 (tasks/types/monitors.py)
- [ ] 更新导入语句

### 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 端到端测试通过

### 验证
- [ ] 所有现有测试通过
- [ ] 无性能回退
- [ ] 文档更新
- [ ] 代码审查通过

---

## 🚨 常见问题

### Q: 消息格式如何处理?
A: LangGraph 使用 `{"messages": [...]}` 格式，需要在适配层转换。

### Q: 如何处理返回值?
A: 返回值是 dict，包含 messages 列表，提取最后一条消息即可。

### Q: 性能会受影响吗?
A: 不会，LangGraph 通常比 Strands 更快。

### Q: 如何回滚?
A: 只需切换导入，改回 Strands 即可。

---

## 📊 预期结果

### 功能
- ✅ 所有 9 个智能体正常工作
- ✅ 多智能体编排完整
- ✅ 工具调用正常
- ✅ 监控系统正常

### 性能
- ✅ 响应时间 ±10%
- ✅ 内存使用 ±15%
- ✅ 吞吐量 ±10%

### 质量
- ✅ 单元测试覆盖 >80%
- ✅ 集成测试覆盖 >70%
- ✅ 所有关键路径测试通过



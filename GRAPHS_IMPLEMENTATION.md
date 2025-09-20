# FivcAdvisor Graphs Implementation

## 概述

本项目成功实现了使用 LangGraph 重新构建 FivcAdvisor flows 的功能。新的 graphs 模块提供了与现有 flows 模块相同的功能，但使用了 LangGraph 的状态图架构，提供了更好的可视化、调试和状态管理能力。

## 实现的功能

### 1. 核心架构

- **基础类**: `Graph` - 所有图的基类，提供通用功能
- **状态管理**: 使用 TypedDict 定义明确的状态结构
- **图检索器**: `GraphsRetriever` - 管理和检索图类型

### 2. 实现的图类型

#### SimpleGraph (`src/fivcadvisor/graphs/simple.py`)
- **功能**: 处理简单任务的线性流程
- **流程**: 接受用户查询 → 评估复杂度 → 运行简单crew（如果任务简单）
- **状态**: `user_query`, `assessment`, `final_result`, `error`

#### GeneralGraph (`src/fivcadvisor/graphs/general.py`)
- **功能**: 通用任务处理，支持复杂度路由
- **流程**: 接受用户查询 → 评估复杂度 → 路由到简单或复杂处理
- **状态**: `user_query`, `assessment`, `plan`, `final_result`, `error`
- **特色**: 条件路由，根据评估结果自动选择处理路径

#### ComplexGraph (`src/fivcadvisor/graphs/complex.py`)
- **功能**: 专门处理复杂任务
- **流程**: 接受用户查询 → 构建计划 → 执行计划
- **状态**: `user_query`, `plan`, `final_result`, `error`

### 3. 目录结构

```
src/fivcadvisor/graphs/
├── __init__.py              # 主入口，提供创建函数
├── simple.py               # SimpleGraph 实现
├── general.py              # GeneralGraph 实现
├── complex.py              # ComplexGraph 实现
├── README.md               # 详细文档
└── utils/
    ├── __init__.py         # 工具模块入口
    ├── base.py             # 基础Graph类
    └── retrievers.py       # GraphsRetriever类
```

### 4. 示例和测试

```
examples/graphs/
├── simple_graph_example.py    # SimpleGraph 使用示例
├── general_graph_example.py   # GeneralGraph 使用示例
├── complex_graph_example.py   # ComplexGraph 使用示例
└── demo.py                     # 演示脚本（使用mock）

tests/
└── test_graphs.py              # 完整的测试套件
```

## 技术特点

### 1. 与原有flows的兼容性
- **相同的接口**: 提供相同的创建函数和方法签名
- **相同的功能**: 复用现有的crew创建函数和模型
- **相同的行为**: 保持相同的执行逻辑和错误处理

### 2. LangGraph的优势
- **明确的状态管理**: 使用TypedDict定义状态结构
- **可视化支持**: 支持图结构的可视化
- **条件路由**: 支持基于状态的条件分支
- **错误处理**: 内置的错误传播机制
- **异步支持**: 原生支持async/await

### 3. 代码质量
- **类型安全**: 完整的类型注解
- **测试覆盖**: 11个测试用例，100%通过
- **文档完整**: 详细的README和代码注释
- **错误处理**: 完善的异常处理机制

## 使用方法

### 基本使用

```python
from fivcadvisor.graphs import create_general_graph
from fivcadvisor.tools import create_retriever, register_default_tools

# 设置工具
tools_retriever = create_retriever()
register_default_tools(tools_retriever=tools_retriever)

# 创建并运行图
graph = create_general_graph(tools_retriever=tools_retriever, verbose=True)
result = graph.kickoff(inputs={"user_query": "What is machine learning?"})
```

### 异步使用

```python
import asyncio

async def main():
    result = await graph.kickoff_async(inputs={"user_query": "Your query here"})
    print(result)

asyncio.run(main())
```

## 依赖管理

- **新增依赖**: `langgraph>=0.2.0` 已添加到 `pyproject.toml`
- **兼容性**: 与现有依赖完全兼容
- **安装**: 使用 `uv sync` 自动安装所有依赖

## 测试结果

```bash
$ uv run pytest tests/test_graphs.py -v
================= 11 passed in 7.40s =================
```

所有测试用例均通过，包括：
- 图创建测试
- 输入验证测试  
- 检索器功能测试
- 批量操作测试
- 清理功能测试

## 与flows模块的对比

| 特性 | Flows (CrewAI) | Graphs (LangGraph) |
|------|----------------|-------------------|
| 状态管理 | 实例属性 (`self.state`) | 显式状态传递 |
| 路由 | 装饰器 (`@router`) | 条件边 |
| 错误处理 | 异常机制 | 状态 + 异常 |
| 可视化 | 有限 | 内置图可视化 |
| 异步支持 | 有限 | 原生async/await |
| 调试 | 流程日志 | 状态检查 + 图可视化 |

## 后续扩展

graphs模块的设计支持轻松扩展：

1. **新图类型**: 继承`Graph`类，实现`create_graph`方法
2. **自定义状态**: 定义新的TypedDict状态结构
3. **复杂路由**: 使用条件边实现复杂的决策逻辑
4. **可视化**: 利用LangGraph的可视化功能

## 总结

成功实现了使用LangGraph重构FivcAdvisor flows的目标：

✅ **完整功能**: 实现了SimpleGraph、GeneralGraph、ComplexGraph  
✅ **兼容接口**: 保持与原flows模块相同的API  
✅ **测试覆盖**: 11个测试用例全部通过  
✅ **文档完整**: 提供详细的使用文档和示例  
✅ **依赖管理**: 正确添加LangGraph依赖  
✅ **演示验证**: 提供可运行的演示脚本  

新的graphs模块为FivcAdvisor提供了更强大、更灵活的流程编排能力，同时保持了与现有系统的完全兼容性。

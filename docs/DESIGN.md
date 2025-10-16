# 🚀 FivcAdvisor System Design

> *An intelligent agent ecosystem built on Strands for autonomous tool generation, task assessment, and dynamic agent orchestration*

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [🤖 Agent System](#-agent-system)
- [🧰 Tool Management](#-tool-management)
- [✨ Core Features](#-core-features)
- [🔄 Workflow](#-workflow)

---

## 🎯 Overview

FivcAdvisor is a multi-agent system built on the **Strands framework** that provides intelligent task assessment, dynamic tool retrieval, and flexible agent orchestration. The system uses specialized agents to handle different aspects of task execution, from initial assessment to tool generation and performance evaluation.

### Technology Stack

- **Framework**: Strands (strands-agents)
- **Web Interface**: Streamlit
- **Vector Database**: ChromaDB
- **LLM Support**: OpenAI, Ollama
- **Tool Protocol**: MCP (Model Context Protocol)

---

## 🏗️ Architecture

FivcAdvisor follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (Streamlit Web / CLI)                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Agent Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Companion │  │Consultant│  │ Planner  │  ...        │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Tool Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Calculator│  │  Python  │  │   MCP    │  ...        │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Model Layer                             │
│         (OpenAI / Ollama / Custom)                       │
└─────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Description | Location |
|-----------|-------------|----------|
| **Agents** | Specialized agents for different tasks | `src/fivcadvisor/agents/` |
| **Agent Types** | Runtime models, repositories, monitors | `src/fivcadvisor/agents/types/` |
| **Tools** | Tool management and retrieval system | `src/fivcadvisor/tools/` |
| **Models** | LLM model factories and configuration | `src/fivcadvisor/models.py` |
| **Tasks** | Task execution and orchestration | `src/fivcadvisor/tasks/` |
| **App** | Streamlit web interface | `src/fivcadvisor/app/` |
| **Embeddings** | Vector database for semantic search | `src/fivcadvisor/embeddings/` |
| **Settings** | Configuration management | `src/fivcadvisor/settings/` |
| **Utils** | Utility functions and helpers | `src/fivcadvisor/utils/` |

### Agent Runtime System

FivcAdvisor includes a comprehensive runtime tracking system for agent execution:

**Core Models:**
- `AgentsRuntimeMeta`: Agent configuration and metadata
- `AgentsRuntime`: Complete execution state and history
- `AgentsRuntimeToolCall`: Individual tool invocation records
- `AgentsStatus`: Execution status (PENDING, EXECUTING, COMPLETED, FAILED)

**Repository Pattern:**
- `AgentsRuntimeRepository`: Abstract interface for persistence
- `FileAgentsRuntimeRepository`: File-based JSON storage implementation
- Hierarchical directory structure for organized data storage
- Automatic persistence of all agent interactions

**Storage Structure:**
```
.fivcadvisor/agents/
└── agent_<agent_id>/
    ├── agent.json                    # Agent metadata
    └── run_<timestamp>/
        ├── run.json                  # Runtime execution data
        └── tool_calls/
            └── tool_call_<id>.json   # Tool call records
```

---

## 🤖 Agent System

FivcAdvisor provides a flexible agent system with specialized agents for different purposes:

### Agent Types

#### 1. **Generic Agent**
*Standard agent for general task execution*
- Default agent for most tasks
- Equipped with all available tools
- Flexible and adaptable to various scenarios

#### 2. **Companion Agent**
*Friendly chat agent for conversations*
- Optimized for natural dialogue
- Uses chat-optimized LLM models
- Maintains conversation context
- Ideal for interactive sessions

#### 3. **ToolRetriever Agent**
*Specialized in finding the right tools*
- Analyzes task requirements
- Searches tool registry
- Recommends optimal tool combinations
- Uses reasoning-optimized models

#### 4. **Consultant Agent**
*Assesses tasks and recommends approaches*
- Evaluates task complexity
- Determines if planning is needed
- Identifies required tools
- Provides direct answers for simple queries

#### 5. **Planner Agent**
*Creates execution plans and teams*
- Breaks down complex tasks
- Designs specialized agent teams
- Assigns tools to team members
- Coordinates multi-agent workflows

#### 6. **Researcher Agent**
*Analyzes patterns and workflows*
- Identifies recurring task sequences
- Analyzes execution patterns
- Extracts insights from logs
- Supports continuous improvement

#### 7. **Engineer Agent**
*Develops and optimizes tools*
- Creates composite tools
- Combines existing functionalities
- Implements new capabilities
- Maintains tool ecosystem

#### 8. **Evaluator Agent**
*Assesses performance and quality*
- Monitors agent performance
- Evaluates tool effectiveness
- Provides improvement feedback
- Validates new implementations

#### 9. **Generic Swarm**
*Multi-agent team for complex tasks*
- Coordinates multiple specialized agents
- Distributes work across team members
- Manages inter-agent communication
- Aggregates results

### Agent Creation

Agents are created using factory functions with the `@agent_creator` decorator:

```python
from fivcadvisor import agents

# Create a generic agent
agent = agents.create_default_agent()

# Create a specialized agent
consultant = agents.create_consultant_agent()

# Create with custom configuration
custom_agent = agents.create_default_agent(
    name="CustomAgent",
    system_prompt="You are a specialized assistant...",
    tools=[tool1, tool2]
)
```

---

## 🧰 Tool Management

### Tool System

FivcAdvisor uses a flexible tool management system:

**Built-in Tools:**
- `calculator` - Mathematical calculations
- `current_time` - Date and time information
- `python_repl` - Python code execution

**MCP Tools:**
- Dynamically loaded from MCP servers
- Configured via `configs/mcp.yaml`
- Supports any MCP-compatible tool

### Tool Retrieval

The `ToolsRetriever` provides semantic search over available tools:

```python
from fivcadvisor import tools

# Get all tools
all_tools = tools.default_retriever.get_all()

# Get specific tools
selected_tools = tools.default_retriever.get_batch(["calculator", "python_repl"])

# Search for relevant tools
relevant_tools = tools.default_retriever.retrieve("I need to calculate something")
```

---

## ✨ Core Features

### 1. **Intelligent Task Assessment**
- Automatic complexity evaluation
- Tool requirement identification
- Planning necessity determination
- Direct answer provision for simple queries

### 2. **Dynamic Tool Management**
- Automatic tool discovery and registration
- MCP protocol support
- Semantic tool search
- Tool combination and composition

### 3. **Flexible Agent Orchestration**
- Multiple specialized agent types
- Dynamic agent creation
- Multi-agent coordination (Swarm)
- Conversation management

### 4. **Interactive Web Interface**
- Multi-page navigation with Streamlit
- Multiple concurrent chat sessions
- Real-time streaming responses
- Async execution support
- Tool usage visualization
- Persistent conversation history
- Component-based UI architecture

### 5. **Comprehensive Persistence**
- File-based agent runtime storage
- Complete execution history tracking
- Tool call recording and replay
- JSON-based human-readable format
- Hierarchical directory organization

### 6. **Extensible Architecture**
- Plugin-based tool system
- Custom agent creation with decorators
- Multiple LLM provider support
- Modular component design
- Repository pattern for data storage
- Event-driven monitoring system

---

## 🔄 Workflow

### Basic Execution Flow

```
1. User Input
   ↓
2. Agent Selection
   ↓
3. Task Assessment (Consultant)
   ↓
4. Tool Retrieval (if needed)
   ↓
5. Execution (Generic/Specialized Agent)
   ↓
6. Result Delivery
```

### Complex Task Flow

```
1. User Input
   ↓
2. Consultant Assessment
   ↓
3. Planning Required?
   ├─ Yes → Planner Agent
   │         ↓
   │      Team Creation
   │         ↓
   │      Swarm Execution
   │         ↓
   └─ No → Direct Execution
   ↓
4. Result Aggregation
   ↓
5. Evaluation (optional)
   ↓
6. Result Delivery
```

### Tool Generation Flow (Future)

```
1. Pattern Recognition (Researcher)
   ↓
2. Tool Design (Engineer)
   ↓
3. Implementation
   ↓
4. Evaluation (Evaluator)
   ↓
5. Registration (if approved)
   ↓
6. Monitoring & Optimization
```

---

## 🏗️ Web Application Architecture

### Multi-Page Structure

FivcAdvisor's web interface uses Streamlit's navigation system for a modern multi-page experience:

```
Web Application
├── Chats (Dynamic Pages)
│   ├── New Chat (Create new conversation)
│   └── Chat Pages (One per existing chat)
└── Settings
    └── Configuration & Management
```

### Component Hierarchy

```
app/__init__.py (Main Application)
├── ChatManager (Multi-chat orchestration)
│   └── Chat Instances (Individual conversations)
│       ├── AgentsRuntimeRepository (Persistence)
│       ├── ToolsRetriever (Tool access)
│       └── Agent Execution (Strands agents)
├── Views (Page rendering)
│   ├── chats.render(chat)
│   ├── settings.render()
│   └── tasks.render()
└── Components (Reusable UI)
    └── chat_message.render(runtime, container)
```

### Data Flow

```
User Input
    ↓
Chat View (views/chats.py)
    ↓
Chat.ask(query, on_event=callback)
    ↓
Agent Execution (async)
    ↓
Streaming Updates → on_event callback
    ↓
Component Rendering (chat_message)
    ↓
Repository Persistence (FileAgentsRuntimeRepository)
    ↓
UI Update (st.rerun)
```

---

## 🚀 Future Enhancements

- **Autonomous Tool Generation**: Automatic creation of composite tools
- **Performance Optimization**: ML-based decision optimization
- **Enhanced Evaluation**: Comprehensive performance metrics
- **Pattern Learning**: Workflow pattern recognition and optimization
- **Human-in-the-Loop**: Interactive validation and feedback
- **Task Monitoring Dashboard**: Real-time task execution visualization
- **Multi-Agent Collaboration**: Enhanced swarm coordination
- **Database Backend**: Optional database repository implementation

---

**Last Updated**: 2025-10-16
**Version**: 0.1.0
**Framework**: Strands (strands-agents 1.9.1+)

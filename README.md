# FivcAdvisor

An intelligent agent ecosystem built on the Strands framework for autonomous tool generation, task assessment, and dynamic agent orchestration.

## 🎯 Overview

FivcAdvisor provides a flexible multi-agent system that can:
- **Assess tasks** intelligently to determine the best approach
- **Retrieve and use tools** dynamically based on task requirements
- **Plan and execute** complex workflows with specialized agents
- **Generate and optimize** tools autonomously
- **Chat and assist** users through an interactive web interface

## 🚀 Quickstart

### Prerequisites
- Python 3.10 or higher
- API keys for LLM providers (OpenAI, Ollama, etc.)

### Installation

```bash
# Install with uv (recommended)
make install        # runtime + dev dependencies

# Or minimal installation
make install-min    # runtime only

# Or with pip
pip install -e .
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Configure your LLM provider settings in `.env`:
```bash
# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Or Ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### Quick Start

```bash
# Launch the web interface
make serve

# Or run an agent from CLI
uv run fivcadvisor run Generic --query "What is machine learning?"

# Show available commands
uv run fivcadvisor --help
```

## 📁 Project Structure

```
src/fivcadvisor/
├── agents/          # Agent creation and management
│   └── types/       # Agent retriever and creator types
├── app/             # Streamlit web interface
├── embeddings/      # Vector database and embeddings
│   └── types/       # Embedding database types
├── models.py        # LLM model factories
├── schemas.py       # Pydantic data schemas
├── settings/        # Configuration management
├── tasks.py         # Task execution functions
├── tools/           # Tool management and retrieval
│   └── types/       # Tool retriever and config types
└── utils/           # Utility functions

configs/             # Configuration examples
examples/            # Usage examples
├── agents/          # Agent usage examples
└── tools/           # Tool usage examples
tests/               # Test suite
docs/                # Documentation
```

## 💻 Usage

### Command Line Interface

```bash
# Show all available commands
fivcadvisor --help

# Run an agent interactively
fivcadvisor run Generic

# Run an agent with a specific query
fivcadvisor run Generic --query "What is machine learning?"

# Run different agent types
fivcadvisor run Companion --query "Tell me a joke"
fivcadvisor run Consultant --query "How should I approach this task?"

# Clean temporary files
fivcadvisor clean

# Show system information
fivcadvisor info
```

### Available Agents

- **Generic** - Standard agent for general task execution
- **Companion** - Friendly chat agent for conversations
- **ToolRetriever** - Specialized in finding the right tools
- **Consultant** - Assesses tasks and recommends approaches
- **Planner** - Creates execution plans and teams
- **Researcher** - Analyzes patterns and workflows
- **Engineer** - Develops and optimizes tools
- **Evaluator** - Assesses performance and quality

### Web Interface

FivcAdvisor includes a modern web interface built with Streamlit:

```bash
# Launch web interface (default: localhost:8501)
fivcadvisor web

# Or using Make
make serve

# Development mode with auto-reload
make serve-dev

# Custom port and host
fivcadvisor web --port 8080 --host 0.0.0.0
```

**Features:**
- 💬 **Interactive chat interface** - Natural conversation with agents
- 🔄 **Async execution** - Non-blocking, responsive interface
- 🛠️ **Tool integration** - Automatic tool selection and execution
- 📝 **Conversation history** - Full session management
- 🎨 **Modern UI** - Clean, intuitive Streamlit interface

See [Web Interface Documentation](docs/WEB_INTERFACE.md) for detailed usage instructions.

## 🧰 Available Tools

FivcAdvisor includes built-in tools and supports MCP (Model Context Protocol) tools:

**Built-in Tools:**
- `calculator` - Mathematical calculations
- `current_time` - Current date and time
- `python_repl` - Python code execution

**MCP Tools:**
Configure MCP servers in `configs/mcp.yaml` to add additional tools dynamically.

## 📚 Documentation

For comprehensive documentation, see the [docs/](docs/) directory:

- **[System Design](docs/DESIGN.md)** - Architecture and design principles
- **[Web Interface Guide](docs/WEB_INTERFACE.md)** - Complete web interface usage
- **[Dependencies](docs/DEPENDENCIES.md)** - Installation and dependency management
- **[Documentation Index](docs/README.md)** - Complete documentation overview

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

MIT

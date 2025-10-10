# Technology Stack

## Project Type

FivcAdvisor is a **multi-interface AI agent system** that combines:
- **CLI Tool** - Command-line interface for direct agent interaction
- **Web Application** - Streamlit-based interactive chat interface
- **Python Library** - Reusable components for agent and tool management

## Core Technologies

### Primary Language(s)
- **Language**: Python 3.10+
- **Runtime**: CPython (standard Python interpreter)
- **Language-specific tools**: 
  - **Package Manager**: uv (recommended), pip (fallback)
  - **Build System**: setuptools via pyproject.toml
  - **Lock File**: uv.lock for reproducible builds

### Key Dependencies/Libraries

**Agent Framework:**
- **strands-agents** (>=1.9.1): Core AI agent framework providing Agent, Task, Crew, and Flow abstractions
- **strands-agents-tools** (>=0.2.8): Pre-built tools library for agent capabilities

**LLM Integration:**
- **openai** (>=1.109.1): OpenAI API client for GPT models
- **Ollama support**: Via strands.models.ollama for local LLM deployment

**Web Interface:**
- **streamlit** (>=1.49.1): Modern web UI framework with async support and real-time updates

**CLI & Terminal:**
- **typer** (>=0.12.3): Modern CLI framework with type hints
- **rich** (>=13.7.1): Rich terminal formatting and output

**Data & Validation:**
- **pydantic** (>=2.7.0): Data validation and settings management with type safety
- **PyYAML** (>=6.0.1): YAML configuration file parsing

**Vector Database & Embeddings:**
- **chromadb** (>=1.1.0): Vector database for semantic tool search and retrieval
- **langchain-text-splitters** (>=0.3.11): Text processing and chunking utilities

**HTTP & Networking:**
- **httpx** (>=0.28.1): Modern async HTTP client

**Configuration:**
- **python-dotenv** (>=1.0.1): Environment variable management from .env files

**Tool Protocol:**
- **MCP (Model Context Protocol)**: Dynamic tool loading via stdio and SSE clients
- **mcp library**: Integrated via strands.tools.mcp for MCPClient support

**Development Dependencies:**
- **pytest** (>=8.2.0): Testing framework
- **pytest-asyncio** (>=0.21.0): Async test support
- **pytest-cov** (>=4.1.0): Code coverage reporting
- **ruff** (>=0.4.0, <0.6): Fast Python linter and formatter

### Application Architecture

**Modular Plugin-Based Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                  Interface Layer                         │
│         (CLI via Typer / Web via Streamlit)             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Agent Layer                             │
│  - Agent Creators (decorator-based factories)           │
│  - Agent Types (Generic, Companion, Consultant, etc.)   │
│  - Conversation Management                               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Tool Layer                              │
│  - ToolsRetriever (semantic search)                     │
│  - ToolsConfig (MCP integration)                        │
│  - Built-in Tools + MCP Tools                           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Model Layer                             │
│  - Model Factories (default, chat, reasoning, coding)   │
│  - Provider Abstraction (OpenAI, Ollama)                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Infrastructure Layer                        │
│  - Settings Management (YAML + .env)                    │
│  - Embeddings (ChromaDB)                                │
│  - Utilities (lazy loading, directories)                │
└─────────────────────────────────────────────────────────┘
```

**Key Architectural Patterns:**
- **Factory Pattern**: Agent creators with `@agent_creator` decorator
- **Lazy Loading**: Deferred initialization for configuration and resources
- **Plugin System**: Dynamic tool registration and discovery
- **Async/Await**: Non-blocking execution in web interface
- **Separation of Concerns**: Clear boundaries between agents, tools, models, and UI

### Data Storage

- **Primary storage**: File system (YAML configs, .env files, pickle for REPL state)
- **Vector Database**: ChromaDB for tool embeddings and semantic search
  - In-memory or persistent mode
  - Stores tool descriptions and metadata
  - Enables similarity-based tool retrieval
- **Session State**: Streamlit session state for web UI persistence
- **Data formats**: 
  - YAML for configuration (settings.yaml, mcp.yaml)
  - JSON for structured data exchange
  - Pickle for Python object serialization (REPL state)

### External Integrations

**APIs:**
- **OpenAI API**: GPT models for agent intelligence
- **Ollama API**: Local LLM deployment (optional)
- **MCP Servers**: Dynamic tool providers via Model Context Protocol

**Protocols:**
- **HTTP/REST**: OpenAI and Ollama API communication via httpx
- **MCP Protocol**: 
  - Stdio-based communication for local MCP servers
  - SSE (Server-Sent Events) for remote MCP servers
- **WebSocket**: Potential for real-time updates (Streamlit native)

**Authentication:**
- **API Keys**: OpenAI API key via environment variables
- **Environment-based**: All credentials managed through .env files
- **No built-in auth**: Local deployment model (future: add user authentication)

### Monitoring & Dashboard Technologies

**Dashboard Framework:**
- **Streamlit**: Python-native web framework with reactive components
- **Multi-page architecture**: Separate views for chat, settings, etc.
- **Component-based UI**: Reusable message renderers and tool callbacks

**Real-time Communication:**
- **Async Execution**: Python asyncio for non-blocking agent execution
- **Streaming Responses**: Real-time message streaming in chat interface
- **Session Management**: Streamlit session state for conversation persistence

**Visualization Libraries:**
- **Rich**: Terminal-based formatting and progress indicators (CLI)
- **Streamlit Components**: Native UI elements (chat messages, forms, metrics)

**State Management:**
- **Streamlit Session State**: In-memory state for web sessions
- **ChatSession Class**: Manages conversation history and context
- **File System**: Configuration as source of truth (YAML files)

## Development Environment

### Build & Development Tools

- **Build System**: setuptools with pyproject.toml (PEP 621 compliant)
- **Package Management**: 
  - **uv** (recommended): Fast, modern Python package manager
  - **pip**: Fallback for traditional workflows
- **Development workflow**: 
  - **Makefile**: Common commands (install, test, serve, clean)
  - **Hot reload**: Streamlit auto-reload on file changes (`make serve-dev`)
  - **REPL**: Python REPL with state persistence (repl_state.pkl)

**Make Targets:**
```bash
make install      # Install with dev dependencies
make install-min  # Runtime only
make test         # Run pytest suite
make serve        # Launch Streamlit web interface
make serve-dev    # Development mode with auto-reload
make clean        # Remove temporary files
```

### Code Quality Tools

- **Static Analysis**: Ruff (fast Python linter)
- **Formatting**: Ruff (replaces Black and isort)
- **Testing Framework**: 
  - pytest for unit and integration tests
  - pytest-asyncio for async test support
  - pytest-cov for coverage reporting
- **Documentation**: 
  - Markdown documentation in docs/
  - Inline docstrings (Google style)
  - README-driven development

**Test Configuration:**
- Suppress third-party deprecation warnings
- Strict markers and config enforcement
- Verbose output for debugging
- Test discovery: `test_*.py` pattern

### Version Control & Collaboration

- **VCS**: Git
- **Branching Strategy**: Feature branches with main as stable
- **Code Review Process**: Pull requests with review before merge
- **Repository Structure**: 
  - src/ layout for clean package structure
  - Separate configs/, examples/, tests/, docs/

### Dashboard Development

- **Live Reload**: Streamlit watch mode with automatic rerun
- **Port Management**: 
  - Default: localhost:8501
  - Configurable via `--port` and `--host` flags
- **Multi-Instance Support**: Can run multiple Streamlit instances on different ports
- **Development Mode**: `make serve-dev` for enhanced debugging

## Deployment & Distribution

- **Target Platform(s)**: 
  - **Primary**: macOS, Linux (development and production)
  - **Secondary**: Windows (community support)
  - **Deployment**: Local installation, no cloud hosting required
  
- **Distribution Method**: 
  - **PyPI** (future): pip install fivcadvisor
  - **Git Clone**: Direct repository installation
  - **uv**: Fast installation via uv sync
  
- **Installation Requirements**: 
  - Python 3.10 or higher
  - API keys for LLM providers (OpenAI or Ollama)
  - Optional: Node.js for MCP tools (e.g., Playwright)
  
- **Update Mechanism**: 
  - Git pull for development
  - pip/uv upgrade for package updates
  - Lock file (uv.lock) ensures reproducible builds

## Technical Requirements & Constraints

### Performance Requirements

- **Response Time**: 
  - CLI: < 100ms startup time
  - Web UI: < 2s page load
  - Agent execution: Depends on LLM latency (typically 2-10s)
  
- **Memory Usage**: 
  - Base: ~100MB for Python runtime
  - ChromaDB: ~50-200MB depending on tool count
  - Streamlit: ~50-100MB for web interface
  
- **Startup Time**: 
  - CLI: < 1s for simple commands
  - Web UI: 2-5s for Streamlit initialization
  - Tool loading: 1-3s for MCP client initialization

### Compatibility Requirements  

- **Platform Support**: 
  - macOS (primary development platform)
  - Linux (Ubuntu 20.04+, Debian, Fedora)
  - Windows (community support, may require WSL)
  
- **Dependency Versions**: 
  - Python: >=3.10 (required for modern type hints)
  - Core dependencies: Minimum versions specified with >=
  - Lock file ensures exact versions for reproducibility
  
- **Standards Compliance**: 
  - PEP 621: pyproject.toml metadata
  - MCP Protocol: Model Context Protocol specification
  - OpenAI API: Compatible with OpenAI API v1

### Security & Compliance

- **Security Requirements**: 
  - API keys stored in .env files (not committed to git)
  - No built-in authentication (local deployment model)
  - HTTPS for external API calls (OpenAI)
  
- **Compliance Standards**: 
  - No specific compliance requirements (general-purpose tool)
  - User responsible for data handling in their use cases
  
- **Threat Model**: 
  - **Local execution**: Assumes trusted local environment
  - **API key protection**: Users must secure their .env files
  - **Code execution**: Python REPL tool can execute arbitrary code (use with caution)
  - **MCP tools**: External tools run with user's permissions

### Scalability & Reliability

- **Expected Load**: 
  - Single-user local deployment
  - 1-10 concurrent agent executions
  - 10-100 tools in registry
  
- **Availability Requirements**: 
  - No uptime requirements (local tool)
  - Graceful degradation if LLM API unavailable
  
- **Growth Projections**: 
  - Tool library: 50-200 tools over time
  - Agent types: 10-20 specialized agents
  - User base: Individual developers to small teams

## Technical Decisions & Rationale

### Decision Log

1. **Strands Framework over CrewAI**
   - **Why**: Strands provides cleaner abstractions and better MCP integration
   - **Alternatives**: CrewAI (original), LangChain, AutoGen
   - **Trade-offs**: Smaller community but more flexible architecture

2. **Streamlit for Web UI**
   - **Why**: Python-native, rapid development, built-in async support
   - **Alternatives**: Flask/FastAPI + React, Gradio
   - **Trade-offs**: Less customizable than React but much faster to develop

3. **ChromaDB for Vector Storage**
   - **Why**: Lightweight, embeddable, good Python integration
   - **Alternatives**: Pinecone, Weaviate, FAISS
   - **Trade-offs**: Limited scalability but perfect for local deployment

4. **uv for Package Management**
   - **Why**: 10-100x faster than pip, modern dependency resolution
   - **Alternatives**: pip, poetry, pdm
   - **Trade-offs**: Newer tool but significant performance benefits

5. **MCP Protocol for Tool Integration**
   - **Why**: Standard protocol, wide tool ecosystem, dynamic loading
   - **Alternatives**: Custom tool API, LangChain tools
   - **Trade-offs**: Requires MCP server setup but enables rich tool ecosystem

6. **Decorator-based Agent Creation**
   - **Why**: Clean API, type safety, easy registration
   - **Alternatives**: Class-based factories, configuration files
   - **Trade-offs**: More Python-specific but very ergonomic

7. **YAML + .env for Configuration**
   - **Why**: Human-readable, standard formats, environment separation
   - **Alternatives**: TOML, JSON, pure Python
   - **Trade-offs**: Requires parsing but widely understood

## Known Limitations

- **Single-user focus**: No multi-user support or authentication
  - **Impact**: Cannot be deployed as shared service
  - **Future**: Add user management and access control for team deployments

- **Local deployment only**: No cloud hosting or remote access
  - **Impact**: Users must run locally or manage their own hosting
  - **Future**: Add tunnel features or cloud deployment options

- **Limited tool generation**: Autonomous tool creation not yet implemented
  - **Impact**: Users must manually add tools or use MCP servers
  - **Future**: Implement Researcher + Engineer agent workflow for tool generation

- **No persistent conversation history**: Sessions cleared on restart
  - **Impact**: Cannot resume conversations across sessions
  - **Future**: Add database-backed conversation storage

- **Synchronous MCP initialization**: Tool loading blocks startup
  - **Impact**: Slow startup with many MCP servers
  - **Future**: Implement async tool loading and lazy initialization

- **Limited error recovery**: Agent failures may require restart
  - **Impact**: Poor user experience on errors
  - **Future**: Add retry logic and graceful degradation


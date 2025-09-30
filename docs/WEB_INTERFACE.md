# FivcAdvisor Web Interface

FivcAdvisor includes a modern, interactive web interface built with **Streamlit**, providing an intuitive chat-based way to interact with the intelligent agent ecosystem.

## 🚀 Quick Start

### Launch the Web Interface

```bash
# Using Make (recommended)
make serve

# Using CLI directly
uv run fivcadvisor web

# Development mode with auto-reload
make serve-dev

# With custom options
uv run fivcadvisor web --port 8080 --host 0.0.0.0
```

### Access the Interface

Once started, open your browser and navigate to:
- **Default**: http://localhost:8501
- **Custom**: http://localhost:[your-port]

## ✨ Features

### 💬 Chat Interface
- **Natural Conversation**: Chat-based interaction with the Companion agent
- **Multi-turn Dialogue**: Context-aware conversations with full history
- **Async Execution**: Non-blocking interface that stays responsive
- **Streaming Responses**: Real-time response generation
- **Message History**: Persistent conversation history across sessions

### 🛠️ Tool Integration
- **Automatic Tool Selection**: Agent automatically chooses appropriate tools
- **Tool Execution Tracking**: Visual feedback for tool usage
- **Built-in Tools**: Calculator, Python REPL, time utilities
- **MCP Tools**: Support for external MCP-compatible tools
- **Tool Results Display**: Clear presentation of tool outputs

### 📊 User Interface
- **Clean Design**: Modern, intuitive Streamlit interface
- **Responsive Layout**: Adapts to different screen sizes
- **Sidebar Information**: System status and configuration
- **Message Formatting**: Markdown support for rich text
- **Error Handling**: Graceful error messages and recovery

### 🔄 Session Management
- **Persistent Sessions**: Conversations saved across page reloads
- **Session History**: Access to previous conversations
- **Conversation Summarization**: Automatic context management
- **Session Configuration**: Customizable session settings

## 💡 Example Queries

Try these sample queries to explore FivcAdvisor's capabilities:

### General Questions
- "What is machine learning?"
- "Explain quantum computing in simple terms"
- "What are the benefits of renewable energy?"

### Code Generation
- "Write a Python function to calculate fibonacci numbers"
- "Create a function to sort a list of dictionaries by a key"
- "Show me how to read a CSV file in Python"

### Calculations
- "Calculate the compound interest on $10,000 at 5% for 10 years"
- "What is 15% of 250?"
- "Convert 100 USD to EUR"

### Information
- "What time is it?"
- "Tell me about the history of the internet"
- "Explain how neural networks work"

## 🎨 Interface Layout

The web interface features a clean, single-column layout:

- **Header**: Application title and branding
- **Chat Area**: Scrollable conversation history with user and agent messages
- **Input Box**: Text input for user queries at the bottom
- **Sidebar**: System information and configuration (collapsible)

## 🔧 Development

### Running in Development Mode

```bash
# Development mode with auto-reload
make serve-dev

# Or directly with Streamlit
uv run streamlit run src/fivcadvisor/app/__init__.py --server.port 8501
```

### Architecture

The web interface consists of:

**Main Components:**
- `src/fivcadvisor/app/__init__.py` - Main Streamlit application
- `src/fivcadvisor/app/sessions.py` - Session management
- `src/fivcadvisor/app/tools.py` - Tool tracking and visualization

**Key Features:**
- Async agent execution for responsive UI
- Session persistence with file-based storage
- Tool usage tracking and display
- Streaming response support
- Conversation summarization

### Customization

You can customize the interface by modifying:

1. **Agent Configuration** (`app/sessions.py`):
   - Change the default agent type
   - Modify system prompts
   - Configure conversation management

2. **UI Styling** (`app/__init__.py`):
   - Update page configuration
   - Modify layout and styling
   - Add custom components

3. **Tool Display** (`app/tools.py`):
   - Customize tool visualization
   - Add tool-specific formatting
   - Enhance tool result display

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Change to a different port
uv run fivcadvisor web --port 8080
```

#### Dependencies Not Installed
```bash
# Install all dependencies
uv sync

# Or with make
make install
```

#### API Keys Not Configured
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_key_here
```

#### Slow Startup
- First run may be slower due to:
  - Model initialization
  - Tool loading
  - MCP server connections
- Subsequent runs will be faster

#### Chat Not Responding
1. Check terminal output for error messages
2. Verify API keys are configured correctly
3. Ensure LLM provider is accessible
4. Check network connectivity

#### Session Issues
```bash
# Clear session data
rm -rf .fivcadvisor/sessions/*

# Or clean all temporary files
make clean
```

### Getting Help

- **Terminal Output**: Check for detailed error messages
- **Logs**: Review session logs in `.fivcadvisor/sessions/`
- **Documentation**: Refer to [README.md](../README.md) and [DESIGN.md](DESIGN.md)
- **Issues**: Report bugs on the project repository

## 🔗 Integration

The web interface integrates seamlessly with:

### CLI Integration
```bash
# Launch from CLI
fivcadvisor web

# Or with Make
make serve
```

### Agent System
- Uses the same agent system as CLI
- Shares tool registry
- Consistent behavior across interfaces

### Configuration
- Respects environment variables
- Uses same settings files
- Shares session storage

### Tool System
- Access to all registered tools
- MCP tool support
- Dynamic tool loading

This provides a unified experience across command-line and web interfaces.

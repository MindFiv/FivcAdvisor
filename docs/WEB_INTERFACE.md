# FivcAdvisor Web Interface

FivcAdvisor includes a modern web interface built with Streamlit, providing an intuitive chat-based way to interact with the intelligent agent ecosystem.

## Quick Start

### Launch the Web Interface

```bash
# Using Make (recommended)
make serve

# Using CLI directly
uv run fivcadvisor web

# Development mode
make serve-dev

# With custom options
uv run fivcadvisor web --port 8080 --host 0.0.0.0
```

### Access the Interface

Once started, open your browser and navigate to:
- Default: http://localhost:8501

## Features

### 💬 Chat Interface
- **Conversational AI**: Natural chat-based interaction with the agent
- **Multi-turn Conversations**: Context-aware dialogue with conversation history
- **Real-time Processing**: Instant message processing and response generation
- **Message History**: Full conversation history with clear user/agent distinction

### 🎯 Query Processing
- **Graph Selection**: Choose from available graph types:
  - **General**: Intelligent task complexity assessment and execution
  - **Simple**: Simple task execution with basic crew
  - **Complex**: Complex task execution with advanced planning
- **Verbose Mode**: Toggle detailed logging for debugging

### 📊 Results Display
- **Formatted Responses**: Markdown-formatted responses with rich text support
- **JSON Visualization**: Clean display of complex data structures
- **Success/Error Indicators**: Clear visual feedback with emojis and styling
- **Conversation Flow**: Seamless integration of responses into chat history

### ⚙️ Configuration
- **Sidebar Controls**: Easy access to settings and configuration
- **Graph Information**: Dynamic descriptions of selected graph types
- **Example Queries**: One-click example queries to get started quickly
- **Clear Chat**: Reset conversation history for fresh interactions

## Example Queries

Try these sample queries to explore FivcAdvisor's capabilities:

- "What is machine learning?"
- "Write a Python function to calculate fibonacci numbers"
- "Explain the benefits of renewable energy"
- "Create a simple web scraping script"
- "What are the latest trends in AI?"

## Interface Layout

The web interface uses a modern, responsive two-column layout:

- **Left Column (Main)**: Chat interface with conversation history and message input
- **Right Column (Sidebar)**: Configuration panel, graph information, and example queries

## Development

### Running in Development Mode

```bash
# Development mode
make serve-dev

# Or directly with Python
uv run python src/fivcadvisor/app/__init__.py
```

### Customization

The web interface is implemented in `src/fivcadvisor/app/__init__.py` as a single, clean module that:

- Integrates directly with FivcAdvisor's backend
- Provides a modern chat-based user experience
- Supports all graph types and execution modes
- Handles errors gracefully with user-friendly messages
- Uses Gradio's theming system for consistent styling

## Troubleshooting

### Common Issues

1. **Port already in use**: Change port with `uv run fivcadvisor web --port 7861`
2. **Backend not available**: Ensure dependencies are installed with `uv sync`
3. **Slow startup**: First run may be slower due to model initialization
4. **Chat not responding**: Check console for error messages and ensure API keys are configured

### Getting Help

- Check the terminal output for detailed error messages
- Use verbose mode for debugging
- Refer to the main README.md for general troubleshooting

## Integration

The web interface integrates seamlessly with:

- **CLI Commands**: Launched via `fivcadvisor web`
- **Make Targets**: `make serve` and `make serve-dev`
- **Backend Graphs**: Direct integration with all graph types
- **Configuration**: Respects environment variables and settings

This provides a unified experience across command-line and web interfaces.

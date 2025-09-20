# FivcAdvisor Web Interface

FivcAdvisor now includes a modern web interface built with Streamlit, providing an intuitive way to interact with the intelligent agent ecosystem.

## Quick Start

### Launch the Web Interface

```bash
# Start with default settings (localhost:8501)
fivcadvisor web

# Specify custom port and host
fivcadvisor web --port 8080 --host 0.0.0.0

# Run in debug mode
fivcadvisor web --debug
```

### Access the Interface

Once started, open your browser and navigate to:
- Default: http://localhost:8501
- Custom: http://your-host:your-port

## Features

### 🎯 Flow Execution
- **Interactive Query Input**: Enter your queries through a user-friendly text area
- **Flow Type Selection**: Choose from available flows (general, simple, complex)
- **Real-time Progress**: Visual progress indicators during flow execution
- **Verbose Mode**: Toggle detailed logging for debugging

### 📊 Results Display
- **Structured Results**: JSON and text output formatting
- **Success/Error Indicators**: Clear visual feedback on flow execution status
- **Metadata Display**: Flow type, timestamp, and execution details

### 📈 Flow History
- **Execution History**: Track all your previous flow runs
- **Expandable Results**: Click to view detailed results from past executions
- **Query Preview**: Quick preview of queries with truncation for long text

### ⚙️ Configuration
- **Sidebar Controls**: Easy access to settings and flow information
- **Flow Information**: Descriptions and details about available flows
- **History Management**: Clear history with one click

## Interface Layout

### Main Area
- **Query Interface**: Large text area for entering queries
- **Run Button**: Execute flows with visual feedback
- **Latest Result**: Display of the most recent execution result

### Sidebar
- **Configuration Panel**: Flow type selection and verbose mode toggle
- **Flow Information**: Details about selected flow and available options
- **History Controls**: Clear history and view flow descriptions

### History Panel
- **Recent Executions**: Last 10 flow runs with expandable details
- **Quick Access**: Click to view full results from previous runs
- **Status Indicators**: Visual success/error indicators

## Flow Types

### General Flow
- **Description**: Intelligent task complexity assessment and execution
- **Use Case**: Most versatile option for various types of queries
- **Features**: Automatic complexity assessment and appropriate crew assembly

### Simple Flow
- **Description**: Simple task execution with basic crew
- **Use Case**: Straightforward queries that don't require complex planning
- **Features**: Quick execution with minimal overhead

### Complex Flow
- **Description**: Complex task execution with advanced planning
- **Use Case**: Multi-step tasks requiring detailed planning and coordination
- **Features**: Advanced planning crew and sophisticated task orchestration

## Tips for Best Results

### Query Writing
- **Be Specific**: Provide clear, detailed queries for better results
- **Context**: Include relevant context and background information
- **Goals**: Clearly state what you want to achieve

### Flow Selection
- **Start Simple**: Try the general flow first for most queries
- **Escalate**: Use complex flow for multi-step or planning-heavy tasks
- **Debug**: Enable verbose mode when troubleshooting

### Monitoring
- **Watch Progress**: Use the progress indicators to monitor execution
- **Check History**: Review past executions to understand patterns
- **Error Handling**: Check error messages for troubleshooting guidance

## Troubleshooting

### Common Issues

#### Web Interface Won't Start
```bash
# Check if Streamlit is installed
pip list | grep streamlit

# Install if missing
pip install streamlit

# Check port availability
lsof -i :8501
```

#### Flow Execution Errors
- **API Keys**: Ensure your .env file contains required API keys
- **Dependencies**: Run `uv sync` to install all dependencies
- **Verbose Mode**: Enable verbose logging to see detailed error information

#### Performance Issues
- **Port Conflicts**: Try a different port with `--port` option
- **Memory**: Close other applications if experiencing slowdowns
- **Network**: Check firewall settings if accessing remotely

### Getting Help

1. **Check Logs**: Enable verbose mode for detailed execution logs
2. **Review History**: Look at successful executions for comparison
3. **CLI Alternative**: Use `fivcadvisor run` command for debugging
4. **Documentation**: Refer to the main README for additional information

## Development

### Running in Development Mode

```bash
# Install development dependencies
uv sync --extra dev

# Run with debug mode
fivcadvisor web --debug

# Direct Streamlit execution
uv run streamlit run src/fivcadvisor/app.py
```

### Customization

The web interface is built with Streamlit and can be customized by modifying `src/fivcadvisor/app.py`. Key areas for customization:

- **Styling**: Modify the Streamlit configuration and CSS
- **Layout**: Adjust column layouts and component organization
- **Features**: Add new functionality or modify existing behavior
- **Flows**: Integrate additional flow types or modify existing ones

## Security Considerations

### Local Development
- Default configuration binds to localhost only
- No authentication required for local use
- API keys loaded from .env file

### Production Deployment
- Use `--host 0.0.0.0` carefully in production
- Consider adding authentication mechanisms
- Secure API key management
- Network security and firewall configuration

---

For more information about FivcAdvisor flows and capabilities, see the main [README.md](../README.md) and [DESIGN.md](DESIGN.md) documentation.

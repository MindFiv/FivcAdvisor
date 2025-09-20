# FivcAdvisor

Pattern-driven flows and tools on top of CrewAI. Use small, reusable patterns to compose effective agent task flows without heavy upfront planning.

## Quickstart

1. Ensure Python 3.10+
2. Install deps with uv (recommended):

```bash
make install        # runtime + dev + CrewAI extras
# or
make install-min    # runtime only (no dev/crewai extras)
```

3. Try a dry-run of the sample flow (works without CrewAI installed):

```bash
make sample
```

To actually run agents with CrewAI, ensure extras are installed (via `make install` or `make crewai`) and set API keys in `.env` (see `.env.example`):

```bash
make crewai
```

Dev tools (ruff, pytest):

```bash
make dev
```

## Layout

- `src/fivcadvisor/` core library
  - `patterns/` reusable task-patterns
  - `flows/` flow orchestrators
  - `agents/` agent construction helpers
  - `tools/` basic tool wrappers
- `configs/` configs for sample/demo
- `tests/` minimal smoke tests

## Usage

### Command Line Interface

```bash
# Show all available commands
fivcadvisor --help

# Run a flow interactively
fivcadvisor run general

# Run a flow with a specific query
fivcadvisor run general --query "What is machine learning?"

# Generate flow visualization
fivcadvisor plot general

# Clean temporary files
fivcadvisor clean

# Show system information
fivcadvisor info
```

### Web Interface

FivcAdvisor includes a modern web interface built with Streamlit:

```bash
# Launch web interface (default: localhost:8501)
fivcadvisor web

# Custom port and host
fivcadvisor web --port 8080 --host 0.0.0.0

# Debug mode
fivcadvisor web --debug
```

The web interface provides:
- Interactive query input with real-time feedback
- Flow type selection and configuration
- Execution history and result visualization
- Progress monitoring and error handling

See [Web Interface Documentation](docs/WEB_INTERFACE.md) for detailed usage instructions.

## Documentation

For comprehensive documentation, see the [docs/](docs/) directory:

- **[Web Interface Guide](docs/WEB_INTERFACE.md)**: Complete web interface usage guide
- **[System Design](docs/DESIGN.md)**: Architecture and design principles
- **[Implementation Details](docs/STREAMLIT_IMPLEMENTATION.md)**: Technical implementation guide
- **[Flow Documentation](docs/DEFAULT_FLOW.md)**: Flow patterns and development
- **[Documentation Index](docs/README.md)**: Complete documentation overview

## License
MIT

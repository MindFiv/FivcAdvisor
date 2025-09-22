# FivcAdvisor Dependencies Guide

This document explains the dependency structure and installation options for FivcAdvisor.

## 📁 Dependency Management

FivcAdvisor uses modern Python dependency management with:
- **`pyproject.toml`** - Primary dependency specification (source of truth)
- **`uv.lock`** - Lock file for reproducible builds
- **`uv`** - Fast Python package manager (recommended)

## 🚀 Installation Options

### 1. Using UV (Recommended)
For the best experience with fast dependency resolution:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Basic installation
uv sync

# With development dependencies
uv sync --extra dev
```

### 2. Using Make (Convenient)
We provide convenient Make targets:

```bash
# Basic installation
make install

# Minimal installation (runtime only)
make install-min

# Development installation
make dev
```

### 3. Using pip (Traditional)
If you prefer using pip:

```bash
# Basic installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## 📦 Dependency Categories

### Core Runtime Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| typer | >=0.12.3 | CLI framework |
| rich | >=13.7.1 | Terminal formatting |
| gradio | >=4.0.0 | Web interface |
| crewai | >=0.5.0 | AI orchestration |
| langgraph | >=0.2.0 | Graph workflows |
| pydantic | >=2.7.0 | Data validation |
| PyYAML | >=6.0.1 | Configuration files |
| python-dotenv | >=1.0.1 | Environment variables |
| httpx | >=0.28.1 | HTTP client |

### Development Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=8.2.0 | Testing framework |
| ruff | >=0.4.0,<0.6 | Linting and formatting |

## 🔧 Dependency Management

### Updating Dependencies
1. Update `pyproject.toml` (source of truth)
2. Run `uv sync` to update lock file
3. Test in clean environment

### Adding New Dependencies
1. Add to appropriate section in `pyproject.toml`
2. Run `uv sync` to install and update lock file
3. Test installation in clean environment
4. Update this documentation

### Version Pinning Strategy
- **Core dependencies**: Use minimum versions with `>=`
- **Development tools**: Pin to specific ranges when needed
- **Lock file**: Provides exact versions for reproducible builds

## 🔍 Troubleshooting

### Common Issues
1. **Python version**: FivcAdvisor requires Python 3.10+
2. **UV installation**: Install uv from https://astral.sh/uv/
3. **Virtual environment**: UV automatically manages virtual environments

### Solutions
```bash
# Check Python version
python --version

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clean install
rm -rf .venv uv.lock
uv sync

# Check installation
uv run fivcadvisor --help
```

## 📊 Dependency Analysis
To analyze dependencies:

```bash
# Show dependency tree
uv tree

# Show outdated packages
uv sync --upgrade

# Export requirements for compatibility
uv export --format requirements-txt > requirements.txt
```

## 🔄 Maintenance

### Regular Tasks
- **Monthly**: Run `uv sync --upgrade` to check for updates
- **Before releases**: Full dependency audit and testing
- **Security**: Monitor for security advisories

### Best Practices
- Always use `uv sync` after pulling changes
- Keep `uv.lock` in version control for reproducible builds
- Test in clean environments before releases

This modern dependency management ensures FivcAdvisor remains maintainable and secure.

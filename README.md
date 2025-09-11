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

## CLI

```bash
fivcadvisor --help
fivcadvisor run-sample --help
```

## License
MIT

.PHONY: install install-min dev lint format test sample

# Default install: runtime + dev
# Use `make install-min` for a minimal (runtime-only) install
install:
	uv sync --extra dev

# Minimal install: only core runtime deps
install-min:
	uv sync

dev:
	uv sync --extra dev

lint: dev
	uv run ruff check src tests

format: dev
	uv run ruff format src tests

test: dev
	uv run python -m pytest -q

sample:
	uv run hatchery --config configs/sample.yaml --dry-run

#!/usr/bin/env python3
"""
Tests for the tools/types/configs module.
"""

import os
import tempfile
import pytest

from fivcadvisor.tools.types.configs import ToolsConfig


class TestToolsConfig:
    """Test the ToolsConfig class."""

    def test_init_nonexistent_file(self):
        """Test initialization with non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "nonexistent.yaml")
            config = ToolsConfig(config_path)

            assert config.configs == {}
            assert config.clients == []
            assert len(config.errors) > 0

    def test_init_with_yaml_file(self):
        """Test initialization with existing YAML file."""
        yaml_content = """
mcpServers:
  test_server:
    command: python
    args:
      - test.py
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            config_path = f.name

        try:
            config = ToolsConfig(config_path)

            assert "mcpServers" in config.configs
            assert "test_server" in config.configs["mcpServers"]
        finally:
            os.unlink(config_path)

    def test_get_clients(self):
        """Test getting clients."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.yaml")
            config = ToolsConfig(config_path)

            clients = config.get_clients()

            assert isinstance(clients, list)

    def test_load_yaml_file_method(self):
        """Test _load_yaml_file method."""
        yaml_content = """
test_key: test_value
number: 42
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            config_path = f.name

        try:
            config = ToolsConfig(config_path)
            result = config._load_yaml_file(config_path)

            assert result["test_key"] == "test_value"
            assert result["number"] == 42
        finally:
            os.unlink(config_path)

    def test_load_json_file_method(self):
        """Test _load_json_file method."""
        json_content = """
{
  "test_key": "test_value",
  "number": 42
}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(json_content)
            f.flush()
            config_path = f.name

        try:
            config = ToolsConfig(config_path)
            result = config._load_json_file(config_path)

            assert result["test_key"] == "test_value"
            assert result["number"] == 42
        finally:
            os.unlink(config_path)

    def test_empty_yaml_file(self):
        """Test handling of empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()
            config_path = f.name

        try:
            config = ToolsConfig(config_path)

            assert config.configs == {}
            assert len(config.errors) > 0
        finally:
            os.unlink(config_path)

    def test_invalid_yaml_file(self):
        """Test handling of invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            config_path = f.name

        try:
            config = ToolsConfig(config_path)

            assert isinstance(config.configs, dict)
            assert len(config.errors) > 0
        finally:
            os.unlink(config_path)

    def test_unsupported_file_type(self):
        """Test initialization with unsupported file type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.txt")
            config = ToolsConfig(config_path)

            assert config.configs == {}
            assert len(config.errors) > 0


if __name__ == "__main__":
    pytest.main([__file__])

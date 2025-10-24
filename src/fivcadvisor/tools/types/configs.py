import os
from typing import Optional, List, Dict

from mcp import StdioServerParameters, stdio_client
from mcp.client.sse import sse_client
from strands.tools.mcp import MCPClient


class ToolsConfigValue(dict):
    def __init__(self, *args, **kwargs):
        """Initialize ToolsConfigValue, ensuring it's initialized with a dict.

        Raises:
            ValueError: If the value cannot be converted to a dict.
        """
        # Handle case where a non-dict value is passed
        if args and not isinstance(args[0], dict):
            raise ValueError(
                f"ToolsConfigValue must be initialized with a dict, got {type(args[0]).__name__}"
            )
        super().__init__(*args, **kwargs)

    def validate(self) -> bool:
        """Validate that the configuration has required fields.

        A valid configuration must have either:
        - 'command' key for stdio-based MCP servers
        - 'url' key for SSE-based MCP servers

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if not isinstance(self, dict):
            return False

        # Must have either 'command' or 'url'
        has_command = "command" in self
        has_url = "url" in self

        if not (has_command or has_url):
            return False

        # If command-based, validate command and optional args/env
        if has_command:
            command = self.get("command")
            if not isinstance(command, str) or not command:
                return False

            args = self.get("args")
            if args is not None and not isinstance(args, list):
                return False

            env = self.get("env")
            if env is not None and not isinstance(env, dict):
                return False

        # If URL-based, validate URL
        if has_url:
            url = self.get("url")
            if not isinstance(url, str) or not url:
                return False

        # Validate optional bundle field
        bundle = self.get("bundle")
        if bundle is not None and not isinstance(bundle, str):
            return False

        return True

    def get_client(self) -> Optional[MCPClient]:
        """Create and return an MCPClient based on the configuration.

        Supports two types of MCP server configurations:
        1. Command-based: Runs a local command with optional args and env vars
        2. URL-based: Connects to an SSE (Server-Sent Events) endpoint

        Returns:
            MCPClient: An initialized MCPClient instance, or None if config is invalid.

        Raises:
            ValueError: If the configuration format is invalid.
        """
        if not self.validate():
            return None

        if "command" in self:
            # Command-based configuration
            command = self["command"]
            args = self.get("args") or []
            env = self.get("env") or {}

            # Merge with environment variables
            env.update(os.environ)

            return MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(command=command, args=args, env=env)
                )
            )

        elif "url" in self:
            # URL-based configuration
            url = self["url"]
            return MCPClient(lambda: sse_client(url))

        else:
            return None


class ToolsConfig(object):
    """Configuration loader for MCP (Model Context Protocol) servers.

    Loads and manages MCP server configurations from YAML or JSON files.
    Supports parsing server configurations and saving them back to disk.
    """

    def __init__(self, config_file: str = "mcp.yaml"):
        """Initialize ToolsConfig with a configuration file.

        Args:
            config_file: Path to the configuration file (YAML or JSON).
                        Defaults to "mcp.yaml" in the current working directory.
        """
        self._errors = []
        self._config_file = os.path.abspath(os.path.join(os.getcwd(), config_file))
        self._configs: Dict[str, ToolsConfigValue] = {}
        self.load()

        if self._errors:
            print(
                f"Errors loading config: {self._errors},"
                f" in directory: {os.getcwd()}"
            )

    def list(self) -> List[str]:
        return list(self._configs.keys())

    def get(self, name: str) -> Optional[ToolsConfigValue]:
        return self._configs.get(name)

    def set(self, name: str, config: ToolsConfigValue | dict) -> bool:
        if not isinstance(config, ToolsConfigValue):
            config = ToolsConfigValue(config)

        if not config.validate():
            return False

        self._configs[name] = config
        return True

    def delete(self, name: str):
        self._configs.pop(name, None)

    def get_clients(self):
        return [c.get_client() for c in self._configs.values()]

    def get_errors(self):
        """Get list of errors encountered during configuration loading.

        Returns:
            List of exceptions that occurred during loading or parsing.
        """
        return self._errors

    def save(self, filename: Optional[str] = None) -> None:
        """Save the current configuration to a file.

        Args:
            filename: Path to save the configuration to. If None, saves to the
                     original config_file path. File extension determines format
                     (YAML for .yaml/.yml, JSON for .json).
        """
        if filename is None:
            filename = self._config_file
        self._save_file(filename)

    def load(self, filename: Optional[str] = None) -> None:
        if filename is None:
            filename = self._config_file

        # Clear configs but preserve any errors from _load_file
        self._configs.clear()

        configs = self._load_file(filename)

        for k, v in configs.items():
            # Store all configs as-is (can be dicts or ToolsConfigValue)
            # Only validate if it's a dict that looks like an MCP config
            if isinstance(v, dict):
                # Try to validate as MCP config
                try:
                    config_value = ToolsConfigValue(v)
                    if config_value.validate():
                        self._configs[k] = config_value
                    else:
                        # Store as regular dict if not a valid MCP config
                        self._configs[k] = v
                except ValueError:
                    # Store as regular dict if can't be converted to ToolsConfigValue
                    self._configs[k] = v
            else:
                # Non-dict values are stored as-is
                self._configs[k] = v

    def _load_yaml_file(self, filename):
        """Load configuration from a YAML file.

        Args:
            filename: Path to the YAML file to load.

        Returns:
            Dictionary containing the parsed configuration, or empty dict on error.
        """
        import yaml

        try:
            with open(filename, "r") as f:
                conf = yaml.safe_load(f)
                if conf is None:
                    self._errors.append(
                        ValueError(f"Empty or invalid YAML file: {filename}")
                    )
                    return {}
                assert isinstance(conf, dict)
                return conf
        except (
            AssertionError,
            FileNotFoundError,
            ValueError,
            TypeError,
            yaml.YAMLError,
        ) as e:
            self._errors.append(e)
            return {}

    def _load_json_file(self, filename):
        """Load configuration from a JSON file.

        Args:
            filename: Path to the JSON file to load.

        Returns:
            Dictionary containing the parsed configuration, or empty dict on error.
        """
        import json

        try:
            with open(filename, "r") as f:
                conf = json.load(f)
                if conf is None:
                    self._errors.append(
                        ValueError(f"Empty or invalid JSON file: {filename}")
                    )
                    return {}
                assert isinstance(conf, dict)
                return conf
        except (
            AssertionError,
            FileNotFoundError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as e:
            self._errors.append(e)
            return {}

    def _load_file(self, filename):
        """Load configuration from a file based on its extension.

        Determines the file format (YAML or JSON) based on the file extension
        and calls the appropriate load method.

        Args:
            filename: Path to the file to load. Extension determines format.

        Returns:
            Dictionary containing the parsed configuration, or empty dict on error.
        """
        ext = filename.split(".")[-1]
        if ext in ["yml", "yaml"]:
            return self._load_yaml_file(filename)
        elif ext == "json":
            return self._load_json_file(filename)
        else:
            self._errors.append(ValueError(f"Unsupported config file type: {ext}"))
            return {}

    def _save_yaml_file(self, filename: str):
        """Save configuration to a YAML file.

        Args:
            filename: Path to the YAML file to save to.
        """
        import yaml

        try:
            # Convert ToolsConfigValue objects to regular dicts for YAML serialization
            configs_to_save = {
                k: dict(v) if isinstance(v, ToolsConfigValue) else v
                for k, v in self._configs.items()
            }
            with open(filename, "w") as f:
                yaml.safe_dump(configs_to_save, f)
        except (
            AssertionError,
            FileNotFoundError,
            ValueError,
            TypeError,
            yaml.YAMLError,
        ) as e:
            self._errors.append(e)

    def _save_json_file(self, filename: str):
        """Save configuration to a JSON file.

        Args:
            filename: Path to the JSON file to save to.
        """
        import json

        try:
            # Convert ToolsConfigValue objects to regular dicts for JSON serialization
            with open(filename, "w") as f:
                json.dump(self._configs, f)
        except (
            AssertionError,
            FileNotFoundError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as e:
            self._errors.append(e)

    def _save_file(self, filename: str):
        """Save configuration to a file based on its extension.

        Determines the file format (YAML or JSON) based on the file extension
        and calls the appropriate save method.

        Args:
            filename: Path to the file to save to. Extension determines format.
        """
        ext = filename.split(".")[-1]
        if ext in ["yml", "yaml"]:
            self._save_yaml_file(filename)
        elif ext == "json":
            self._save_json_file(filename)
        else:
            self._errors.append(ValueError(f"Unsupported config file type: {ext}"))

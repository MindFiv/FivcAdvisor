import os

from mcp import StdioServerParameters, stdio_client
from mcp.client.sse import sse_client
from strands.tools.mcp import MCPClient


class ToolsConfig(object):
    def __init__(self, config_file: str = "mcp.yaml"):
        self.errors = []
        self.configs = self._load_file(config_file) or {}
        self.clients = self._parse_config() or []
        if self.errors:
            print(
                f"Errors loading config: {self.errors}," f" in directory: {os.getcwd()}"
            )

    def get_clients(self):
        return self.clients

    def _load_yaml_file(self, filename):
        import yaml

        try:
            with open(filename, "r") as f:
                conf = yaml.safe_load(f)
                assert isinstance(conf, dict)
                return conf
        except (
            AssertionError,
            FileNotFoundError,
            ValueError,
            TypeError,
            yaml.YAMLError,
        ) as e:
            self.errors.append(e)
            return {}

    def _load_json_file(self, filename):
        import json

        try:
            with open(filename, "r") as f:
                conf = json.load(f)
                assert isinstance(conf, dict)
                return conf
        except (
            AssertionError,
            FileNotFoundError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as e:
            self.errors.append(e)
            return {}

    def _load_file(self, filename):
        ext = filename.split(".")[-1]
        if ext in ["yml", "yaml"]:
            return self._load_yaml_file(filename)
        elif ext == "json":
            return self._load_json_file(filename)
        else:
            self.errors.append(ValueError(f"Unsupported config file type: {ext}"))
            return {}

    def _parse_config(self):
        if not self.configs:
            return None

        def _parse(c):
            assert isinstance(c, dict)
            if "command" in c:
                c_args = c.get("args") or []
                c_env = c.get("env") or {}

                assert isinstance(c_args, list)
                assert isinstance(c_env, dict)

                c_env.update(**os.environ)

                return MCPClient(
                    lambda: stdio_client(
                        StdioServerParameters(
                            command=c["command"], args=c_args, env=c_env
                        )
                    )
                )

            elif "url" in c:
                return MCPClient(lambda: sse_client(c["url"]))

            else:
                self.errors.append(AssertionError("invalid mcp format"))
                return None

        try:
            return [_parse(v) for _, v in self.configs.items()]
        except (ValueError, TypeError, AssertionError) as e:
            self.errors.append(e)
            return None

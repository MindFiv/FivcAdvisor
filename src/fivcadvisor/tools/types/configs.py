import json
import os

from mcp import StdioServerParameters, stdio_client
from mcp.client.sse import sse_client
from strands.tools.mcp import MCPClient


class ToolsConfig(object):
    def __init__(self, config_file: str = "mcp.json"):
        self.config_file = config_file
        self.configs = self._load_config() or {}
        self.clients = self._parse_config() or []

    def get_clients(self):
        return self.clients

    def _load_config(self):
        try:
            with open(self.config_file, "r") as f:
                c = json.load(f)
                assert isinstance(c, dict)
                c = c.get("mcpServers", {})
                assert isinstance(c, dict)
                return c
        except (
            FileNotFoundError,
            ValueError,
            AssertionError,
            TypeError,
        ):
            return None

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
                raise AssertionError("invalid mcp format")

        try:
            return [_parse(v) for _, v in self.configs.items()]
        except (ValueError, TypeError, AssertionError):
            return None

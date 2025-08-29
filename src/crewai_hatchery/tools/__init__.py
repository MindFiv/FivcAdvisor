def create_retriever(*args, **kwargs):
    """Create a tools retriever tool."""
    from .retrievers import ToolsRetriever

    return ToolsRetriever(*args, **kwargs)


def create_default_tools(*args, tools_retriever=None, **kwargs):
    from .retrievers import ToolsRetriever

    assert isinstance(tools_retriever, ToolsRetriever)

    from .calculators import basic_calculator
    from .clocks import local_clock
    from .webs import web_searcher, web_scraper

    tools = [
        basic_calculator,
        local_clock,
        web_searcher,
        web_scraper,
    ]
    tools_retriever.add_batch(tools)

    return tools


def create_mcp_tools(*args, tools_retriever=None, config_file="mcp.json", **kwargs):
    """Create tools for MCP server."""
    from .retrievers import ToolsRetriever

    assert isinstance(tools_retriever, ToolsRetriever)

    import json
    import os

    from mcp import StdioServerParameters
    from crewai_tools import MCPServerAdapter

    def _get_config(filename):
        try:
            with open(filename, "r") as f:
                c = json.load(f)
                assert isinstance(c, list)
                return c
        except (
            FileNotFoundError,
            ValueError,
            AssertionError,
            TypeError,
        ):
            return None

    def _get_params(config_list):
        def _convert(c):
            assert isinstance(c, dict)
            if "command" not in c:
                return c

            c_cmd = c.get("command") or ""
            c_args = c.get("args") or []
            c_env = c.get("env") or {}

            assert isinstance(c_args, list)
            assert isinstance(c_env, dict)

            c_env.update(**os.environ)

            return StdioServerParameters(command=c_cmd, args=c_args, env=c_env)

        try:
            return [_convert(i) for i in config_list]
        except (ValueError, TypeError, AssertionError):
            return None

    configs = _get_config(config_file)
    config_params = configs and _get_params(configs)
    if not config_params:
        return None

    mcp = MCPServerAdapter(config_params)
    for t in mcp.tools:
        tools_retriever.add(t)

    return mcp

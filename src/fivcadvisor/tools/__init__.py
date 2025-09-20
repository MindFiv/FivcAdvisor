from fivcadvisor import utils


def create_retriever(*args, **kwargs):
    """Create a tools retriever tool."""
    from .utils.retrievers import ToolsRetriever

    return ToolsRetriever(*args, **kwargs)


def register_default_tools(tools_retriever=None, **kwargs):
    assert tools_retriever is not None

    from .calculators import basic_calculator
    from .time import local_time
    from .webs import web_searcher, web_scraper

    tools = [
        basic_calculator,
        # date_calculator,
        local_time,
        web_searcher,
        web_scraper,
    ]
    tools_retriever.add_batch(tools)

    return tools


def register_mcp_tools(tools_retriever=None, config_file="mcp.json", **kwargs):
    """Create tools for MCP server."""
    assert tools_retriever is not None

    import json
    import os

    from mcp import StdioServerParameters
    from crewai_tools import MCPServerAdapter

    def _get_config(filename):
        try:
            with open(filename, "r") as f:
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

    def _get_params(config_dict):
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
            return [_convert(v) for _, v in config_dict.items()]
        except (ValueError, TypeError, AssertionError):
            return None

    configs = _get_config(config_file)
    config_params = configs and _get_params(configs)
    if not config_params:
        return None

    mcp = MCPServerAdapter(config_params)
    tools = list(t for t in mcp.tools)
    tools_retriever.add_batch(tools)

    return mcp


def _load():
    retriever = create_retriever()
    register_default_tools(tools_retriever=retriever)
    # register_mcp_tools(tools_retriever=retriever)
    return retriever


default_retriever = utils.create_lazy_value(_load)

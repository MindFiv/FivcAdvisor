__all__ = [
    "config",
    "default_embedder_config",
    "default_llm_config",
    "chat_llm_config",
    "reasoning_llm_config",
    "coding_llm_config",
    "agent_logger_config",
    "default_logger_config",
]

from fivcadvisor.utils import (
    create_lazy_value,
    create_default_kwargs,
)


def _load_yaml_file(filename):
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
    ):
        print(f"Failed to load config from {filename}")
        return {}


def _load_json_file(filename):
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
    ):
        print(f"Failed to load config from {filename}")
        return {}


def _load_file(filename):
    ext = filename.split(".")[-1]
    if ext in ["yml", "yaml"]:
        return _load_yaml_file(filename)
    elif ext == "json":
        return _load_json_file(filename)
    else:
        raise ValueError(f"Unsupported config file type: {ext}")


def _load():
    import os

    config_file = os.environ.get("CONFIG_FILE", "config.yaml")
    config_file = os.path.abspath(config_file)
    return _load_file(config_file)


config = create_lazy_value(_load)

default_embedder_config = create_lazy_value(
    lambda: create_default_kwargs(
        config.get("default_embedder") or {},
        {
            "provider": "openai",
            "model": "text-embedding-v3",
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "dimension": 1024,
        },
    )
)

default_llm_config = create_lazy_value(
    lambda: create_default_kwargs(
        config.get("default_llm") or {},
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "temperature": 0.5,
        },
    )
)

chat_llm_config = create_lazy_value(
    lambda: create_default_kwargs(
        config.get("chat_llm") or {},
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "temperature": 1.0,
        },
    )
)

reasoning_llm_config = create_lazy_value(
    lambda: create_default_kwargs(
        config.get("reasoning_llm") or {},
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "temperature": 0.1,
        },
    )
)

coding_llm_config = create_lazy_value(
    lambda: create_default_kwargs(
        config.get("coding_llm") or {},
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "temperature": 0.1,
        },
    )
)

agent_logger_config = create_lazy_value(
    lambda: create_default_kwargs(
        config.get("agent_logger") or {},
        {
            "level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
    )
)

default_logger_config = create_lazy_value(
    lambda: create_default_kwargs(
        config.get("default_logger") or {},
        {
            "level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
    )
)

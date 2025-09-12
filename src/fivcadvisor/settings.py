from fivcadvisor.utils import (
    create_lazy_value,
    create_default_kwargs,
)


def _load_yaml_file(filename):
    import yaml

    try:
        with open(filename, "r") as f:
            config = yaml.safe_load(f)
            assert isinstance(config, dict)
            return config
    except (
        AssertionError,
        FileNotFoundError,
        ValueError,
        TypeError,
        yaml.YAMLError,
    ):
        return {}


def _load_json_file(filename):
    import json

    try:
        with open(filename, "r") as f:
            config = json.load(f)
            assert isinstance(config, dict)
            return config
    except (
        AssertionError,
        FileNotFoundError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ):
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

    return _load_file(os.environ.get("CONFIG_FILE", "config.yaml"))


default_config = create_lazy_value(_load)

default_embedder_config = create_lazy_value(
    lambda: create_default_kwargs(
        default_config.get("default_embedder") or {},
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
        default_config.get("default_llm") or {},
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
        default_config.get("chat_llm") or {},
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
        default_config.get("reasoning_llm") or {},
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
        default_config.get("coding_llm") or {},
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "temperature": 0.1,
        },
    )
)

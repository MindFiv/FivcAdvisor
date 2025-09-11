from os import environ

from fivcadvisor.utils import create_lazy_value


default_embedder_config = create_lazy_value(
    lambda: {
        "provider": environ.get("DEFAULT_EMBEDDER_PROVIDER") or "openai",
        "model": environ.get("DEFAULT_EMBEDDER_MODEL") or "text-embedding-v3",
        "base_url": environ.get("DEFAULT_EMBEDDER_BASE_URL")
        or "https://api.openai.com/v1",
        "api_key": environ.get("DEFAULT_EMBEDDER_API_KEY"),
        "dimension": 1024,
    }
)


default_llm_config = create_lazy_value(
    lambda: {
        "provider": environ.get("DEFAULT_LLM_PROVIDER") or "openai",
        "model": environ.get("DEFAULT_LLM_MODEL") or "gpt-4o-mini",
        "base_url": environ.get("DEFAULT_LLM_BASE_URL") or "https://api.openai.com/v1",
        "api_key": environ.get("DEFAULT_LLM_API_KEY"),
        "temperature": 0.5,
    }
)


chat_llm_config = create_lazy_value(
    lambda: {
        "provider": environ.get("CHAT_LLM_PROVIDER"),
        "model": environ.get("CHAT_LLM_MODEL"),
        "base_url": environ.get("CHAT_LLM_BASE_URL"),
        "api_key": environ.get("CHAT_LLM_API_KEY"),
        "temperature": 1.0,
    }
)


reasoning_llm_config = create_lazy_value(
    lambda: {
        "provider": environ.get("REASONING_LLM_PROVIDER"),
        "model": environ.get("REASONING_LLM_MODEL"),
        "base_url": environ.get("REASONING_LLM_BASE_URL"),
        "api_key": environ.get("REASONING_LLM_API_KEY"),
        "temperature": 0.1,
    }
)


coding_llm_config = create_lazy_value(
    lambda: {
        "provider": environ.get("CODING_LLM_PROVIDER"),
        "model": environ.get("CODING_LLM_MODEL"),
        "base_url": environ.get("CODING_LLM_BASE_URL"),
        "api_key": environ.get("CODING_LLM_API_KEY"),
        "temperature": 0.1,
    }
)

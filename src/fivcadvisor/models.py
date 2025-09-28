__all__ = [
    "create_default_model",
    "create_chat_model",
    "create_reasoning_model",
    "create_coding_model",
]

from strands.models import Model


def _openai_model(*args, **kwargs) -> Model:
    from strands.models.openai import OpenAIModel

    return OpenAIModel(
        client_args={
            "api_key": kwargs.get("api_key", ""),
            "base_url": kwargs.get("base_url", ""),
        },
        model_id=kwargs.get("model", ""),
        params={
            # "max_tokens": 2000,
            "temperature": kwargs.get("temperature", 0.5)
        },
    )


def _ollama_model(*args, **kwargs) -> Model:
    from strands.models.ollama import OllamaModel

    return OllamaModel(
        kwargs.get("base_url", "http://localhost:8000"),
        model_id=kwargs.get("model", ""),
        temperature=kwargs.get("temperature", 0.5),
    )


def create_default_model(*args, **kwargs) -> Model:
    """
    Factory function to create an LLM instance
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import default_llm_config

    kwargs = create_default_kwargs(kwargs, default_llm_config)

    model_provider = kwargs.pop("provider")
    if not model_provider:
        raise AssertionError("provider not specified")

    # model_id = kwargs.pop("model", "")
    # if not model_id:
    #     raise AssertionError("model not specified")

    if model_provider == "openai":
        return _openai_model(*args, **kwargs)
    if model_provider == "ollama":
        return _ollama_model(*args, **kwargs)
    else:
        raise AssertionError(f"Unsupported model provider: {model_provider}")


def create_chat_model(*args, **kwargs) -> Model:
    """
    Factory function to create an LLM instance for chat
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import chat_llm_config

    return create_default_model(*args, **create_default_kwargs(kwargs, chat_llm_config))


def create_reasoning_model(*args, **kwargs) -> Model:
    """
    Factory function to create an LLM instance for task assessment
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import reasoning_llm_config

    return create_default_model(
        *args, **create_default_kwargs(kwargs, reasoning_llm_config)
    )


def create_coding_model(*args, **kwargs) -> Model:
    """
    Factory function to create an LLM instance for coding tasks
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import coding_llm_config

    return create_default_model(
        *args, **create_default_kwargs(kwargs, coding_llm_config)
    )

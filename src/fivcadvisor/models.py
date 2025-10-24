__all__ = [
    "create_default_model",
    "create_chat_model",
    "create_reasoning_model",
    "create_coding_model",
]

from langchain_core.language_models import LLM


def _openai_model(*args, **kwargs) -> LLM:
    """Create an OpenAI model using LangChain adapter."""
    from .adapters import create_openai_model

    return create_openai_model(**kwargs)


def _ollama_model(*args, **kwargs) -> LLM:
    """Create an Ollama model using LangChain adapter."""
    from .adapters import create_ollama_model

    return create_ollama_model(**kwargs)


def _litellm_model(*args, **kwargs) -> LLM:
    """Create a LiteLLM model using LangChain adapter."""
    from .adapters import create_litellm_model

    return create_litellm_model(**kwargs)


def create_default_model(*args, **kwargs) -> LLM:
    """
    Factory function to create a LangChain LLM instance.

    This function maintains backward compatibility with the Strands model API
    while using LangChain models under the hood.

    Args:
        **kwargs: Model configuration (provider, model, api_key, temperature, etc.)

    Returns:
        LangChain LLM instance

    Raises:
        ValueError: If provider is not specified or unsupported
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import default_llm_config

    kwargs = create_default_kwargs(kwargs, default_llm_config)

    model_provider = kwargs.pop("provider")
    if not model_provider:
        raise ValueError("provider not specified")

    if model_provider == "openai":
        return _openai_model(*args, **kwargs)
    elif model_provider == "ollama":
        return _ollama_model(*args, **kwargs)
    elif model_provider == "litellm":
        return _litellm_model(*args, **kwargs)
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")


def create_chat_model(*args, **kwargs) -> LLM:
    """
    Factory function to create a LangChain LLM instance for chat.

    Uses the chat_llm_config from settings for default configuration.

    Args:
        **kwargs: Model configuration (overrides defaults)

    Returns:
        LangChain LLM instance configured for chat
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import chat_llm_config

    return create_default_model(*args, **create_default_kwargs(kwargs, chat_llm_config))


def create_reasoning_model(*args, **kwargs) -> LLM:
    """
    Factory function to create a LangChain LLM instance for reasoning tasks.

    Uses the reasoning_llm_config from settings for default configuration.

    Args:
        **kwargs: Model configuration (overrides defaults)

    Returns:
        LangChain LLM instance configured for reasoning
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import reasoning_llm_config

    return create_default_model(
        *args, **create_default_kwargs(kwargs, reasoning_llm_config)
    )


def create_coding_model(*args, **kwargs) -> LLM:
    """
    Factory function to create a LangChain LLM instance for coding tasks.

    Uses the coding_llm_config from settings for default configuration.

    Args:
        **kwargs: Model configuration (overrides defaults)

    Returns:
        LangChain LLM instance configured for coding
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import coding_llm_config

    return create_default_model(
        *args, **create_default_kwargs(kwargs, coding_llm_config)
    )

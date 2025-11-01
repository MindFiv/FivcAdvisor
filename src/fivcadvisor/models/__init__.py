__all__ = [
    "create_default_model",
    "create_chat_model",
    "create_reasoning_model",
    "create_coding_model",
]

from typing import Callable

from langchain_core.language_models import BaseChatModel
from fivcadvisor import settings, utils
from fivcadvisor.models.providers import default_providers


def create_default_model(**kwargs) -> BaseChatModel:
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

    kwargs = utils.create_default_kwargs(kwargs, settings.default_llm_config)

    model_provider = default_providers.get(kwargs.get("provider"))
    if not isinstance(model_provider, Callable):
        raise ValueError(f"Unsupported model provider: {kwargs.get('provider')}")

    return model_provider(**kwargs)


def create_chat_model(**kwargs) -> BaseChatModel:
    """
    Factory function to create a LangChain LLM instance for chat.

    Uses the chat_llm_config from settings for default configuration.

    Args:
        **kwargs: Model configuration (overrides defaults)

    Returns:
        LangChain LLM instance configured for chat
    """

    return create_default_model(
        **utils.create_default_kwargs(kwargs, settings.chat_llm_config)
    )


def create_reasoning_model(**kwargs) -> BaseChatModel:
    """
    Factory function to create a LangChain LLM instance for reasoning tasks.

    Uses the reasoning_llm_config from settings for default configuration.

    Args:
        **kwargs: Model configuration (overrides defaults)

    Returns:
        LangChain LLM instance configured for reasoning
    """
    # Set defaults from env if available

    return create_default_model(
        **utils.create_default_kwargs(kwargs, settings.reasoning_llm_config)
    )


def create_coding_model(**kwargs) -> BaseChatModel:
    """
    Factory function to create a LangChain LLM instance for coding tasks.

    Uses the coding_llm_config from settings for default configuration.

    Args:
        **kwargs: Model configuration (overrides defaults)

    Returns:
        LangChain LLM instance configured for coding
    """
    # Set defaults from env if available

    return create_default_model(
        **utils.create_default_kwargs(kwargs, settings.coding_llm_config)
    )

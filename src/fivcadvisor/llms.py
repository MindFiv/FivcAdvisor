__all__ = [
    "create_default_llm",
    "create_chat_llm",
    "create_reasoning_llm",
    "create_coding_llm",
]

from typing import Optional
from crewai import LLM


class _LLM(LLM):
    session_id: Optional[str] = None


def create_default_llm(*args, session_id=None, **kwargs) -> LLM:
    """
    Factory function to create an LLM instance
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import default_llm_config

    kwargs = create_default_kwargs(kwargs, default_llm_config)
    kwargs.setdefault("stream", True)
    model_provider = kwargs.pop("provider", "openai")
    model = kwargs.pop("model", "")
    if not model:
        raise AssertionError("model not specified")

    # using openai compatible mode
    llm = _LLM(f"{model_provider}/{model}", *args, **kwargs)
    llm.session_id = session_id
    return llm


def create_chat_llm(*args, **kwargs) -> LLM:
    """
    Factory function to create an LLM instance for chat
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import chat_llm_config

    return create_default_llm(*args, **create_default_kwargs(kwargs, chat_llm_config))


def create_reasoning_llm(*args, **kwargs) -> LLM:
    """
    Factory function to create an LLM instance for task assessment
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import reasoning_llm_config

    return create_default_llm(
        *args, **create_default_kwargs(kwargs, reasoning_llm_config)
    )


def create_coding_llm(*args, **kwargs) -> LLM:
    """
    Factory function to create an LLM instance for coding tasks
    """
    # Set defaults from env if available
    from .utils import create_default_kwargs
    from .settings import coding_llm_config

    return create_default_llm(*args, **create_default_kwargs(kwargs, coding_llm_config))

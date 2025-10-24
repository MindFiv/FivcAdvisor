"""
LangChain model adapter for multi-provider LLM support.

This module provides a unified interface for creating LangChain models
from various providers (OpenAI, Ollama, LiteLLM) while maintaining
compatibility with the existing Strands model API.
"""

from typing import Any, Dict, Optional, Union
from langchain_core.language_models import LLM


def create_openai_model(**kwargs) -> LLM:
    """
    Create a ChatOpenAI model instance.
    
    Args:
        model: Model name (e.g., "gpt-4", "gpt-4o-mini")
        api_key: OpenAI API key
        base_url: Base URL for OpenAI API (default: https://api.openai.com/v1)
        temperature: Temperature for sampling (0-2)
        max_tokens: Maximum tokens in response
        **kwargs: Additional arguments passed to ChatOpenAI
        
    Returns:
        ChatOpenAI instance
    """
    from langchain_openai import ChatOpenAI
    
    model_name = kwargs.get("model", "gpt-4o-mini")
    api_key = kwargs.get("api_key", "")
    base_url = kwargs.get("base_url", "https://api.openai.com/v1")
    temperature = kwargs.get("temperature", 0.5)
    max_tokens = kwargs.get("max_tokens")
    
    # Build ChatOpenAI kwargs
    openai_kwargs = {
        "model": model_name,
        "temperature": temperature,
    }
    
    if api_key:
        openai_kwargs["api_key"] = api_key
    
    if base_url and base_url != "https://api.openai.com/v1":
        openai_kwargs["base_url"] = base_url
    
    if max_tokens:
        openai_kwargs["max_tokens"] = max_tokens
    
    # Pass through any additional kwargs
    for key in kwargs:
        if key not in ["model", "api_key", "base_url", "temperature", "max_tokens", "provider"]:
            openai_kwargs[key] = kwargs[key]
    
    return ChatOpenAI(**openai_kwargs)


def create_ollama_model(**kwargs) -> LLM:
    """
    Create an Ollama model instance.
    
    Args:
        model: Model name (e.g., "llama2", "mistral")
        base_url: Ollama server URL (default: http://localhost:11434)
        temperature: Temperature for sampling (0-2)
        **kwargs: Additional arguments passed to Ollama
        
    Returns:
        Ollama instance
    """
    from langchain_community.llms import Ollama
    
    model_name = kwargs.get("model", "llama2")
    base_url = kwargs.get("base_url", "http://localhost:11434")
    temperature = kwargs.get("temperature", 0.5)
    
    # Build Ollama kwargs
    ollama_kwargs = {
        "model": model_name,
        "base_url": base_url,
        "temperature": temperature,
    }
    
    # Pass through any additional kwargs
    for key in kwargs:
        if key not in ["model", "base_url", "temperature", "provider"]:
            ollama_kwargs[key] = kwargs[key]
    
    return Ollama(**ollama_kwargs)


def create_litellm_model(**kwargs) -> LLM:
    """
    Create a LiteLLM model instance.
    
    Args:
        model: Model name (e.g., "gpt-4", "claude-3-opus")
        api_key: API key for the provider
        base_url: Base URL for the provider (optional)
        temperature: Temperature for sampling (0-2)
        **kwargs: Additional arguments passed to LiteLLM
        
    Returns:
        LiteLLM instance
    """
    from langchain_community.llms import LiteLLM
    
    model_name = kwargs.get("model", "gpt-4o-mini")
    api_key = kwargs.get("api_key", "")
    base_url = kwargs.get("base_url", "")
    temperature = kwargs.get("temperature", 0.5)
    
    # Build LiteLLM kwargs
    litellm_kwargs = {
        "model": model_name,
        "temperature": temperature,
    }
    
    if api_key:
        litellm_kwargs["api_key"] = api_key
    
    if base_url:
        litellm_kwargs["base_url"] = base_url
    
    # Pass through any additional kwargs
    for key in kwargs:
        if key not in ["model", "api_key", "base_url", "temperature", "provider"]:
            litellm_kwargs[key] = kwargs[key]
    
    return LiteLLM(**litellm_kwargs)


def create_langchain_model(provider: str, **kwargs) -> LLM:
    """
    Factory function to create a LangChain model from any provider.
    
    This function provides a unified interface for creating models from
    different providers while maintaining compatibility with the existing
    Strands model API.
    
    Args:
        provider: Model provider ("openai", "ollama", "litellm")
        **kwargs: Provider-specific arguments
        
    Returns:
        LangChain LLM instance
        
    Raises:
        ValueError: If provider is not supported
        
    Example:
        >>> model = create_langchain_model(
        ...     "openai",
        ...     model="gpt-4",
        ...     api_key="sk-...",
        ...     temperature=0.5
        ... )
        >>> model = create_langchain_model(
        ...     "ollama",
        ...     model="llama2",
        ...     base_url="http://localhost:11434"
        ... )
    """
    if provider == "openai":
        return create_openai_model(**kwargs)
    elif provider == "ollama":
        return create_ollama_model(**kwargs)
    elif provider == "litellm":
        return create_litellm_model(**kwargs)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


def create_default_langchain_model(**kwargs) -> LLM:
    """
    Create a default LangChain model using configuration.
    
    This function replaces the Strands create_default_model function
    and uses the same configuration system.
    
    Args:
        **kwargs: Model configuration (provider, model, api_key, etc.)
        
    Returns:
        LangChain LLM instance
    """
    from fivcadvisor.utils import create_default_kwargs
    from fivcadvisor.settings import default_llm_config
    
    # Merge with defaults
    kwargs = create_default_kwargs(kwargs, default_llm_config())
    
    # Extract provider
    provider = kwargs.pop("provider", "openai")
    if not provider:
        raise ValueError("provider not specified")
    
    return create_langchain_model(provider, **kwargs)


def create_chat_langchain_model(**kwargs) -> LLM:
    """
    Create a LangChain model for chat using chat configuration.
    
    Args:
        **kwargs: Model configuration
        
    Returns:
        LangChain LLM instance
    """
    from fivcadvisor.utils import create_default_kwargs
    from fivcadvisor.settings import chat_llm_config
    
    kwargs = create_default_kwargs(kwargs, chat_llm_config())
    return create_default_langchain_model(**kwargs)


def create_reasoning_langchain_model(**kwargs) -> LLM:
    """
    Create a LangChain model for reasoning tasks.
    
    Args:
        **kwargs: Model configuration
        
    Returns:
        LangChain LLM instance
    """
    from fivcadvisor.utils import create_default_kwargs
    from fivcadvisor.settings import reasoning_llm_config
    
    kwargs = create_default_kwargs(kwargs, reasoning_llm_config())
    return create_default_langchain_model(**kwargs)


def create_coding_langchain_model(**kwargs) -> LLM:
    """
    Create a LangChain model for coding tasks.
    
    Args:
        **kwargs: Model configuration
        
    Returns:
        LangChain LLM instance
    """
    from fivcadvisor.utils import create_default_kwargs
    from fivcadvisor.settings import coding_llm_config
    
    kwargs = create_default_kwargs(kwargs, coding_llm_config())
    return create_default_langchain_model(**kwargs)


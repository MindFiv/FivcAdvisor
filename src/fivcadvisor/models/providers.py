from langchain_core.language_models import BaseChatModel


def _openai_model(
    model: str = "gpt-4o-mini",
    api_key: str = "",
    base_url: str = "https://api.openai.com/v1",
    temperature: float = 0.5,
    max_tokens: int = 4096,
    **kwargs,
) -> BaseChatModel:
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

    return ChatOpenAI(
        model=model,
        api_key=lambda: api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _ollama_model(
    model: str = "llama2",
    base_url: str = "http://localhost:11434",
    temperature: float = 0.5,
    reasoning: bool = False,
    **kwargs,
) -> BaseChatModel:
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
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=model,
        base_url=base_url,
        temperature=temperature,
        reasoning=reasoning,
    )


default_providers = {
    "openai": _openai_model,
    "ollama": _ollama_model,
}

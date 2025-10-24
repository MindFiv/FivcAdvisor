"""
Tests for LangChain model adapter.

This module tests the model adapter to ensure it correctly creates
LangChain models from various providers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from fivcadvisor.adapters import (
    create_langchain_model,
    create_default_langchain_model,
    create_chat_langchain_model,
    create_reasoning_langchain_model,
    create_coding_langchain_model,
    create_openai_model,
    create_ollama_model,
    create_litellm_model,
)


class TestFactoryFunction:
    """Test the factory function for creating models."""

    def test_create_langchain_model_openai(self):
        """Test creating OpenAI model via factory."""
        with patch("fivcadvisor.adapters.models.create_openai_model") as mock_create:
            mock_create.return_value = Mock()
            result = create_langchain_model("openai", model="gpt-4")
            mock_create.assert_called_once()
            assert result is not None

    def test_create_langchain_model_ollama(self):
        """Test creating Ollama model via factory."""
        with patch("fivcadvisor.adapters.models.create_ollama_model") as mock_create:
            mock_create.return_value = Mock()
            result = create_langchain_model("ollama", model="llama2")
            mock_create.assert_called_once()
            assert result is not None

    def test_create_langchain_model_litellm(self):
        """Test creating LiteLLM model via factory."""
        with patch("fivcadvisor.adapters.models.create_litellm_model") as mock_create:
            mock_create.return_value = Mock()
            result = create_langchain_model("litellm", model="gpt-4")
            mock_create.assert_called_once()
            assert result is not None

    def test_create_langchain_model_unsupported_provider(self):
        """Test that unsupported provider raises error."""
        with pytest.raises(ValueError, match="Unsupported model provider"):
            create_langchain_model("unsupported_provider")


class TestModelAdapterExports:
    """Test that all model adapter functions are properly exported."""

    def test_all_functions_exported(self):
        """Test that all model functions are exported from adapters."""
        from fivcadvisor import adapters

        # Check all functions are available
        assert hasattr(adapters, "create_langchain_model")
        assert hasattr(adapters, "create_default_langchain_model")
        assert hasattr(adapters, "create_chat_langchain_model")
        assert hasattr(adapters, "create_reasoning_langchain_model")
        assert hasattr(adapters, "create_coding_langchain_model")
        assert hasattr(adapters, "create_openai_model")
        assert hasattr(adapters, "create_ollama_model")
        assert hasattr(adapters, "create_litellm_model")

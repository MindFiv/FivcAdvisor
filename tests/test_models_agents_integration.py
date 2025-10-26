"""
Integration tests for models module with agents module.

Tests verify:
- Agents module correctly imports from models module
- Agent creation functions use the correct model factories
- Model configuration flows through agent creation
- Backward compatibility with agent creation API
"""

from unittest.mock import patch, MagicMock
from langchain_core.language_models import BaseChatModel

from fivcadvisor.agents import (
    create_default_agent,
    create_companion_agent,
    create_tooling_agent,
    create_consultant_agent,
)


class TestAgentsModuleImports:
    """Test that agents module correctly imports from models module."""

    def test_agents_imports_model_factories(self):
        """Test agents module imports model factory functions."""
        from fivcadvisor import agents

        # These should be available through the agents module's imports
        assert hasattr(agents, "create_default_model")
        assert hasattr(agents, "create_chat_model")
        assert hasattr(agents, "create_reasoning_model")

    def test_agents_init_imports_from_models(self):
        """Test agents/__init__.py imports from fivcadvisor.models."""
        import fivcadvisor.agents as agents_module

        # Check that the module has the imported functions in its namespace
        assert "create_default_model" in dir(agents_module)
        assert "create_chat_model" in dir(agents_module)
        assert "create_reasoning_model" in dir(agents_module)


class TestDefaultAgentModelUsage:
    """Test create_default_agent uses create_default_model."""

    @patch("fivcadvisor.agents.create_default_model")
    @patch("fivcadvisor.agents.create_langchain_agent")
    @patch("fivcadvisor.agents.tools")
    def test_default_agent_creates_default_model(
        self, mock_tools, mock_langchain_agent, mock_create_model
    ):
        """Test create_default_agent calls create_default_model."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_create_model.return_value = mock_model
        mock_tools.default_retriever.get_all.return_value = []
        mock_langchain_agent.return_value = MagicMock()

        create_default_agent()

        mock_create_model.assert_called_once()

    @patch("fivcadvisor.agents.create_default_model")
    @patch("fivcadvisor.agents.create_langchain_agent")
    @patch("fivcadvisor.agents.tools")
    def test_default_agent_passes_model_to_langchain_agent(
        self, mock_tools, mock_langchain_agent, mock_create_model
    ):
        """Test create_default_agent passes model to create_langchain_agent."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_create_model.return_value = mock_model
        mock_tools.default_retriever.get_all.return_value = []
        mock_langchain_agent.return_value = MagicMock()

        create_default_agent()

        # Verify model was passed to langchain agent
        call_kwargs = mock_langchain_agent.call_args[1]
        assert call_kwargs["model"] == mock_model

    @patch("fivcadvisor.agents.create_default_model")
    @patch("fivcadvisor.agents.create_langchain_agent")
    @patch("fivcadvisor.agents.tools")
    def test_default_agent_respects_provided_model(
        self, mock_tools, mock_langchain_agent, mock_create_model
    ):
        """Test create_default_agent doesn't override provided model."""
        custom_model = MagicMock(spec=BaseChatModel)
        mock_tools.default_retriever.get_all.return_value = []
        mock_langchain_agent.return_value = MagicMock()

        create_default_agent(model=custom_model)

        # create_default_model should not be called
        mock_create_model.assert_not_called()

        # Custom model should be passed to langchain agent
        call_kwargs = mock_langchain_agent.call_args[1]
        assert call_kwargs["model"] == custom_model


class TestCompanionAgentModelUsage:
    """Test create_companion_agent uses create_chat_model."""

    @patch("fivcadvisor.agents.create_chat_model")
    @patch("fivcadvisor.agents.create_default_agent")
    @patch("fivcadvisor.agents.tools")
    def test_companion_agent_creates_chat_model(
        self, mock_tools, mock_default_agent, mock_create_chat
    ):
        """Test create_companion_agent calls create_chat_model."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_create_chat.return_value = mock_model
        mock_tools.default_retriever.get_all.return_value = []
        mock_default_agent.return_value = MagicMock()

        create_companion_agent()

        mock_create_chat.assert_called_once()

    @patch("fivcadvisor.agents.create_chat_model")
    @patch("fivcadvisor.agents.create_default_agent")
    @patch("fivcadvisor.agents.tools")
    def test_companion_agent_passes_chat_model(
        self, mock_tools, mock_default_agent, mock_create_chat
    ):
        """Test create_companion_agent passes chat model to default agent."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_create_chat.return_value = mock_model
        mock_tools.default_retriever.get_all.return_value = []
        mock_default_agent.return_value = MagicMock()

        create_companion_agent()

        # Verify model was passed to default agent
        call_kwargs = mock_default_agent.call_args[1]
        assert call_kwargs["model"] == mock_model

    @patch("fivcadvisor.agents.create_chat_model")
    @patch("fivcadvisor.agents.create_default_agent")
    @patch("fivcadvisor.agents.tools")
    def test_companion_agent_respects_provided_model(
        self, mock_tools, mock_default_agent, mock_create_chat
    ):
        """Test create_companion_agent doesn't override provided model."""
        custom_model = MagicMock(spec=BaseChatModel)
        mock_tools.default_retriever.get_all.return_value = []
        mock_default_agent.return_value = MagicMock()

        create_companion_agent(model=custom_model)

        # create_chat_model should not be called
        mock_create_chat.assert_not_called()


class TestToolingAgentModelUsage:
    """Test create_tooling_agent uses create_reasoning_model."""

    @patch("fivcadvisor.agents.create_reasoning_model")
    @patch("fivcadvisor.agents.create_default_agent")
    def test_tooling_agent_creates_reasoning_model(
        self, mock_default_agent, mock_create_reasoning
    ):
        """Test create_tooling_agent calls create_reasoning_model."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_create_reasoning.return_value = mock_model
        mock_default_agent.return_value = MagicMock()

        create_tooling_agent()

        mock_create_reasoning.assert_called_once()

    @patch("fivcadvisor.agents.create_reasoning_model")
    @patch("fivcadvisor.agents.create_default_agent")
    def test_tooling_agent_passes_reasoning_model(
        self, mock_default_agent, mock_create_reasoning
    ):
        """Test create_tooling_agent passes reasoning model to default agent."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_create_reasoning.return_value = mock_model
        mock_default_agent.return_value = MagicMock()

        create_tooling_agent()

        # Verify model was passed to default agent
        call_kwargs = mock_default_agent.call_args[1]
        assert call_kwargs["model"] == mock_model


class TestConsultantAgentModelUsage:
    """Test create_consultant_agent uses create_reasoning_model."""

    @patch("fivcadvisor.agents.create_reasoning_model")
    @patch("fivcadvisor.agents.create_default_agent")
    def test_consultant_agent_creates_reasoning_model(
        self, mock_default_agent, mock_create_reasoning
    ):
        """Test create_consultant_agent calls create_reasoning_model."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_create_reasoning.return_value = mock_model
        mock_default_agent.return_value = MagicMock()

        create_consultant_agent()

        mock_create_reasoning.assert_called_once()

    @patch("fivcadvisor.agents.create_reasoning_model")
    @patch("fivcadvisor.agents.create_default_agent")
    def test_consultant_agent_passes_reasoning_model(
        self, mock_default_agent, mock_create_reasoning
    ):
        """Test create_consultant_agent passes reasoning model to default agent."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_create_reasoning.return_value = mock_model
        mock_default_agent.return_value = MagicMock()

        create_consultant_agent()

        # Verify model was passed to default agent
        call_kwargs = mock_default_agent.call_args[1]
        assert call_kwargs["model"] == mock_model


class TestModelMigrationBackwardCompatibility:
    """Test backward compatibility after migration."""

    def test_models_module_is_package(self):
        """Test models is now a package, not a module."""
        import fivcadvisor.models as models

        # Should have __path__ attribute (package indicator)
        assert hasattr(models, "__path__")

    def test_direct_imports_work(self):
        """Test direct imports from models work."""
        from fivcadvisor.models import (
            create_default_model,
            create_chat_model,
            create_reasoning_model,
            create_coding_model,
        )

        assert callable(create_default_model)
        assert callable(create_chat_model)
        assert callable(create_reasoning_model)
        assert callable(create_coding_model)

    def test_providers_accessible(self):
        """Test providers module is accessible."""
        from fivcadvisor.models.providers import default_providers

        assert isinstance(default_providers, dict)
        assert len(default_providers) > 0

    def test_no_old_models_py_file(self):
        """Test old models.py file doesn't exist."""
        import os

        old_models_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "fivcadvisor", "models.py"
        )

        assert not os.path.exists(old_models_path), "Old models.py file still exists"

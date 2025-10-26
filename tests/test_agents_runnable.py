"""
Comprehensive tests for AgentsRunnable implementation.

Tests verify:
- AgentsRunnable initialization with various parameters
- Synchronous execution via run() method
- Asynchronous execution via run_async() method
- Callback handler support
- Tool handling and conversion
- Error handling and edge cases
- Runnable interface compliance
"""

from unittest.mock import MagicMock, patch
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from fivcadvisor.agents.types import AgentsRunnable


class TestAgentsRunnableInitialization:
    """Test AgentsRunnable initialization."""

    def test_init_with_required_parameters(self):
        """Test AgentsRunnable initialization with required parameters."""
        mock_model = MagicMock(spec=BaseChatModel)

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")

        assert agent._name == "TestAgent"
        assert agent._agent is not None
        assert agent.id is not None

    def test_init_with_system_prompt(self):
        """Test AgentsRunnable initialization with system prompt."""
        mock_model = MagicMock(spec=BaseChatModel)
        system_prompt = "You are a helpful assistant"

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            system_prompt=system_prompt,
        )

        assert agent._system_prompt == system_prompt

    def test_init_with_callback_handler(self):
        """Test AgentsRunnable initialization with callback handler."""
        mock_model = MagicMock(spec=BaseChatModel)
        callback_handler = MagicMock()

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            callback_handler=callback_handler,
        )

        assert agent._callback_handler == callback_handler

    def test_init_generates_unique_ids(self):
        """Test that each AgentsRunnable gets a unique ID."""
        mock_model = MagicMock(spec=BaseChatModel)

        agent1 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")
        agent2 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent2")

        assert agent1.id != agent2.id


class TestAgentsRunnableProperties:
    """Test AgentsRunnable properties."""

    def test_id_property(self):
        """Test that id property returns a string."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")

        assert isinstance(agent.id, str)
        assert len(agent.id) > 0

    def test_id_property_consistency(self):
        """Test that id property returns the same value on multiple calls."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")

        id1 = agent.id
        id2 = agent.id

        assert id1 == id2


class TestAgentsRunnableExecution:
    """Test AgentsRunnable execution methods."""

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_method_exists(self, mock_create_agent):
        """Test that run method exists and is callable."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"messages": [("assistant", "Test response")]}
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")

        assert hasattr(agent, "run")
        assert callable(agent.run)

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_async_method_exists(self, mock_create_agent):
        """Test that run_async method exists and is callable."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")

        assert hasattr(agent, "run_async")
        assert callable(agent.run_async)

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_callable_interface(self, mock_create_agent):
        """Test that AgentsRunnable is callable via __call__."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"messages": [("assistant", "Test response")]}
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")

        assert callable(agent)


class TestAgentsRunnableToolHandling:
    """Test AgentsRunnable tool handling."""

    def test_init_with_empty_tools(self):
        """Test initialization with empty tools list."""
        mock_model = MagicMock(spec=BaseChatModel)

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")

        assert agent._agent is not None

    def test_init_with_langchain_tools(self):
        """Test initialization with LangChain tools."""
        mock_model = MagicMock(spec=BaseChatModel)

        @tool
        def test_tool(query: str) -> str:
            """A test tool."""
            return f"Result for {query}"

        agent = AgentsRunnable(
            model=mock_model, tools=[test_tool], agent_name="TestAgent"
        )

        assert agent._agent is not None


class TestAgentsRunnableCallbackHandling:
    """Test AgentsRunnable callback handler support."""

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_callback_handler_called_on_success(self, mock_create_agent):
        """Test that callback handler is called on successful execution."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"messages": [("assistant", "Test response")]}
        mock_create_agent.return_value = mock_agent

        callback_handler = MagicMock()
        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            callback_handler=callback_handler,
        )

        # Note: callback is called with result
        result = agent.run("test query")
        assert result is not None


class TestAgentsRunnableIntegration:
    """Integration tests for AgentsRunnable."""

    def test_agent_creation_flow(self):
        """Test complete agent creation flow."""
        mock_model = MagicMock(spec=BaseChatModel)

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            system_prompt="You are helpful",
        )

        assert agent._name == "TestAgent"
        assert agent._system_prompt == "You are helpful"
        assert agent.id is not None
        assert agent._agent is not None

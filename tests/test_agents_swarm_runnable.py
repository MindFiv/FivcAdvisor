"""
Comprehensive tests for AgentsSwarmRunnable implementation.

Tests verify:
- AgentsSwarmRunnable initialization with various parameters
- Synchronous execution via run() method
- Asynchronous execution via run_async() method
- Agent routing and state management
- Message passing between agents
- Error handling and edge cases
- Runnable interface compliance
"""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.language_models import BaseChatModel

from fivcadvisor.agents.types import AgentsRunnable, AgentsSwarmRunnable


class TestAgentsSwarmRunnableInitialization:
    """Test AgentsSwarmRunnable initialization."""

    def test_init_with_valid_agents(self):
        """Test creating swarm with valid agents."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent1 = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="Agent1",
        )
        agent2 = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="Agent2",
        )

        swarm = AgentsSwarmRunnable(
            swarm_name="TestSwarm",
            agents=[agent1, agent2],
        )

        assert swarm.name == "TestSwarm"
        assert len(swarm.agents) == 2
        assert swarm.agents[0]._name == "Agent1"
        assert swarm.agents[1]._name == "Agent2"

    def test_init_with_auto_generated_id(self):
        """Test that swarm ID is auto-generated if not provided."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")

        swarm = AgentsSwarmRunnable(agents=[agent])

        assert swarm.id is not None
        assert len(swarm.id) > 0

    def test_init_with_custom_id(self):
        """Test creating swarm with custom ID."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")

        swarm = AgentsSwarmRunnable(
            swarm_id="custom-swarm-id",
            agents=[agent],
        )

        assert swarm.id == "custom-swarm-id"

    def test_init_with_default_agent_name(self):
        """Test that default agent name is set correctly."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent1 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")
        agent2 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent2")

        swarm = AgentsSwarmRunnable(
            agents=[agent1, agent2],
            default_agent_name="Agent2",
        )

        assert swarm._default_agent_name == "Agent2"

    def test_init_without_agents_raises_error(self):
        """Test that initialization without agents raises ValueError."""
        with pytest.raises(ValueError, match="At least one agent is required"):
            AgentsSwarmRunnable(agents=[])

    def test_init_with_none_agents_raises_error(self):
        """Test that initialization with None agents raises ValueError."""
        with pytest.raises(ValueError, match="At least one agent is required"):
            AgentsSwarmRunnable(agents=None)

    def test_agent_map_creation(self):
        """Test that agent map is created correctly."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent1 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")
        agent2 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent2")

        swarm = AgentsSwarmRunnable(agents=[agent1, agent2])

        assert "Agent1" in swarm._agent_map
        assert "Agent2" in swarm._agent_map
        assert swarm._agent_map["Agent1"] == agent1
        assert swarm._agent_map["Agent2"] == agent2


class TestAgentsSwarmRunnableProperties:
    """Test AgentsSwarmRunnable properties."""

    def test_id_property(self):
        """Test id property."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")

        swarm = AgentsSwarmRunnable(swarm_id="test-id", agents=[agent])

        assert swarm.id == "test-id"

    def test_name_property(self):
        """Test name property."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")

        swarm = AgentsSwarmRunnable(swarm_name="MySwarm", agents=[agent])

        assert swarm.name == "MySwarm"

    def test_agents_property(self):
        """Test agents property."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent1 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")
        agent2 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent2")

        swarm = AgentsSwarmRunnable(agents=[agent1, agent2])

        assert len(swarm.agents) == 2
        assert swarm.agents[0] == agent1
        assert swarm.agents[1] == agent2


class TestAgentsSwarmRunnableExecution:
    """Test AgentsSwarmRunnable execution methods."""

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_method_exists(self, mock_create_agent):
        """Test that run method exists and is callable."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Test response"}]
        }
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")
        swarm = AgentsSwarmRunnable(agents=[agent])

        assert hasattr(swarm, "run")
        assert callable(swarm.run)

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_async_method_exists(self, mock_create_agent):
        """Test that run_async method exists and is callable."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")
        swarm = AgentsSwarmRunnable(agents=[agent])

        assert hasattr(swarm, "run_async")
        assert callable(swarm.run_async)

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_callable_interface(self, mock_create_agent):
        """Test that AgentsSwarmRunnable is callable via __call__."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Test response"}]
        }
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")
        swarm = AgentsSwarmRunnable(agents=[agent])

        assert callable(swarm)


class TestAgentsSwarmRunnableRouting:
    """Test agent routing logic."""

    def test_route_to_agent_with_next_agent(self):
        """Test routing to next agent when specified."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent1 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")
        agent2 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent2")

        swarm = AgentsSwarmRunnable(agents=[agent1, agent2])

        state = {"next_agent": "Agent2"}
        next_agent = swarm._route_to_agent(state)

        assert next_agent == "Agent2"

    def test_route_to_agent_with_invalid_next_agent(self):
        """Test routing when next_agent is invalid."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")

        swarm = AgentsSwarmRunnable(agents=[agent])

        state = {"next_agent": "InvalidAgent"}
        next_agent = swarm._route_to_agent(state)

        assert next_agent == "END"

    def test_route_to_default_agent(self):
        """Test routing to default agent when no next_agent specified."""
        mock_model = MagicMock(spec=BaseChatModel)
        agent1 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent1")
        agent2 = AgentsRunnable(model=mock_model, tools=[], agent_name="Agent2")

        swarm = AgentsSwarmRunnable(
            agents=[agent1, agent2],
            default_agent_name="Agent2",
        )

        state = {}
        next_agent = swarm._route_to_agent(state)

        assert next_agent == "Agent2"


class TestAgentsSwarmRunnableErrorHandling:
    """Test error handling in swarm execution."""

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_handles_exceptions(self, mock_create_agent):
        """Test that run method handles exceptions gracefully."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_agent.invoke.side_effect = Exception("Test error")
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")
        swarm = AgentsSwarmRunnable(agents=[agent])

        result = swarm.run("test query")

        assert "Swarm error" in result

    @pytest.mark.asyncio
    @patch("fivcadvisor.agents.types.runnables.create_agent")
    async def test_run_async_handles_exceptions(self, mock_create_agent):
        """Test that run_async method handles exceptions gracefully."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()
        mock_agent.ainvoke.side_effect = Exception("Test error")
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(model=mock_model, tools=[], agent_name="TestAgent")
        swarm = AgentsSwarmRunnable(agents=[agent])

        result = await swarm.run_async("test query")

        assert "Swarm error" in result

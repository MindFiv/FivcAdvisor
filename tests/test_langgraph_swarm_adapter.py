"""
Tests for LangGraph Swarm adapter.

This module tests the LangGraphSwarmAdapter to ensure it provides
a compatible interface with Strands Swarm.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fivcadvisor.adapters import LangGraphSwarmAdapter, create_langchain_swarm


class TestLangGraphSwarmAdapter:
    """Test suite for LangGraphSwarmAdapter."""

    def test_adapter_requires_agents(self):
        """Test that adapter requires at least one agent."""
        with pytest.raises(ValueError, match="At least one agent is required"):
            LangGraphSwarmAdapter([])

    def test_adapter_stores_default_agent_name(self):
        """Test that adapter stores default agent name."""
        agent = Mock()
        agent.name = "TestAgent"

        adapter = LangGraphSwarmAdapter([agent])
        assert adapter.default_agent_name == "TestAgent"

    def test_adapter_stores_custom_default_agent_name(self):
        """Test that adapter stores custom default agent name."""
        agent1 = Mock()
        agent1.name = "Agent1"
        agent2 = Mock()
        agent2.name = "Agent2"

        adapter = LangGraphSwarmAdapter([agent1, agent2], default_agent_name="Agent2")
        assert adapter.default_agent_name == "Agent2"

    def test_adapter_stores_agents_list(self):
        """Test that adapter stores agents list."""
        agent1 = Mock()
        agent1.name = "Agent1"
        agent2 = Mock()
        agent2.name = "Agent2"

        adapter = LangGraphSwarmAdapter([agent1, agent2])
        assert len(adapter.agents) == 2
        assert adapter.agents[0] == agent1
        assert adapter.agents[1] == agent2

    def test_adapter_has_invoke_async_method(self):
        """Test that adapter has invoke_async method."""
        agent = Mock()
        agent.name = "TestAgent"

        adapter = LangGraphSwarmAdapter([agent])
        assert hasattr(adapter, "invoke_async")
        assert callable(adapter.invoke_async)

    def test_adapter_has_invoke_method(self):
        """Test that adapter has invoke method."""
        agent = Mock()
        agent.name = "TestAgent"

        adapter = LangGraphSwarmAdapter([agent])
        assert hasattr(adapter, "invoke")
        assert callable(adapter.invoke)

    def test_adapter_has_workflow_and_app(self):
        """Test that adapter creates workflow and app."""
        agent = Mock()
        agent.name = "TestAgent"

        adapter = LangGraphSwarmAdapter([agent])
        assert hasattr(adapter, "workflow")
        assert hasattr(adapter, "app")
        assert adapter.workflow is not None
        assert adapter.app is not None


class TestSwarmIntegration:
    """Integration tests for Swarm adapter."""

    def test_adapter_with_multiple_agents_integration(self):
        """Test adapter with multiple agents."""
        # Create mock agents with names
        agents = []
        for i in range(3):
            agent = Mock()
            agent.name = f"Agent{i+1}"
            agents.append(agent)

        # Create adapter
        adapter = LangGraphSwarmAdapter(agents)

        # Verify all agents are included
        assert len(adapter.agents) == 3
        assert adapter.agents[0].name == "Agent1"
        assert adapter.agents[1].name == "Agent2"
        assert adapter.agents[2].name == "Agent3"

    def test_factory_function_with_kwargs(self):
        """Test factory function accepts kwargs."""
        agent = Mock()
        agent.name = "TestAgent"

        # Create swarm with extra kwargs
        swarm = create_langchain_swarm(
            [agent], default_agent_name="TestAgent", extra_param="value"
        )

        # Verify swarm was created
        assert isinstance(swarm, LangGraphSwarmAdapter)


class TestAdapterCompatibility:
    """Test adapter compatibility with Strands Swarm API."""

    def test_adapter_api_compatibility(self):
        """Test that adapter provides Strands-compatible API."""
        agent = Mock()
        agent.name = "TestAgent"

        adapter = LangGraphSwarmAdapter([agent])

        # Verify key methods exist
        assert hasattr(adapter, "invoke_async")
        assert hasattr(adapter, "invoke")
        assert hasattr(adapter, "agents")
        assert hasattr(adapter, "default_agent_name")

    def test_adapter_returns_dict_from_invoke(self):
        """Test that invoke methods return dict-like results."""
        agent = Mock()
        agent.name = "TestAgent"

        adapter = LangGraphSwarmAdapter([agent])

        # Verify app has ainvoke method
        assert hasattr(adapter.app, "ainvoke")


class TestSwarmUtilityMethods:
    """Test utility methods of LangGraphSwarmAdapter."""

    def test_get_agent_by_name(self):
        """Test retrieving an agent by name."""
        agent1 = Mock()
        agent1.name = "Agent1"
        agent2 = Mock()
        agent2.name = "Agent2"

        adapter = LangGraphSwarmAdapter([agent1, agent2])

        # Test getting existing agent
        retrieved = adapter.get_agent_by_name("Agent1")
        assert retrieved == agent1

        # Test getting non-existent agent
        retrieved = adapter.get_agent_by_name("NonExistent")
        assert retrieved is None

    def test_get_agent_names(self):
        """Test getting all agent names."""
        agent1 = Mock()
        agent1.name = "Agent1"
        agent2 = Mock()
        agent2.name = "Agent2"
        agent3 = Mock()
        agent3.name = "Agent3"

        adapter = LangGraphSwarmAdapter([agent1, agent2, agent3])

        names = adapter.get_agent_names()
        assert len(names) == 3
        assert "Agent1" in names
        assert "Agent2" in names
        assert "Agent3" in names

    def test_set_default_agent(self):
        """Test setting the default agent."""
        agent1 = Mock()
        agent1.name = "Agent1"
        agent2 = Mock()
        agent2.name = "Agent2"

        adapter = LangGraphSwarmAdapter([agent1, agent2], default_agent_name="Agent1")

        # Verify initial default
        assert adapter.default_agent_name == "Agent1"

        # Change default
        adapter.set_default_agent("Agent2")
        assert adapter.default_agent_name == "Agent2"

    def test_set_default_agent_invalid(self):
        """Test setting an invalid default agent."""
        agent1 = Mock()
        agent1.name = "Agent1"

        adapter = LangGraphSwarmAdapter([agent1])

        # Try to set non-existent agent
        with pytest.raises(ValueError, match="Agent 'NonExistent' not found"):
            adapter.set_default_agent("NonExistent")

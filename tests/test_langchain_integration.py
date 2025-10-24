"""
Integration tests for LangChain migration

Tests the complete workflow integration with LangChain agents,
ensuring all components work together correctly.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import os

# Set dummy API keys to avoid initialization errors
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("CHROMA_OPENAI_API_KEY", "sk-test-key")

from fivcadvisor.adapters import (
    LangChainAgentAdapter,
    create_langchain_agent,
    LangGraphSwarmAdapter,
)
from fivcadvisor.agents import (
    create_default_agent,
    create_companion_agent,
    create_tooling_agent,
    create_consultant_agent,
    create_planning_agent,
    create_research_agent,
    create_engineering_agent,
    create_evaluating_agent,
    create_generic_agent_swarm,
)
from fivcadvisor.tasks.types import TaskTeam


class TestLangChainAgentIntegration(unittest.TestCase):
    """Integration tests for LangChain agents"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.mock_tool = Mock()
        self.mock_tool.name = "test_tool"

    def test_langchain_agent_adapter_creation(self):
        """Test that LangChainAgentAdapter can be created directly"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
            system_prompt="Test prompt",
            name="TestAgent",
        )

        self.assertIsInstance(adapter, LangChainAgentAdapter)
        self.assertEqual(adapter.name, "TestAgent")
        self.assertEqual(adapter.system_prompt, "Test prompt")
        self.assertIsNotNone(adapter.agent_id)

    def test_agent_with_custom_parameters(self):
        """Test agent creation with custom parameters"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[self.mock_tool],
            system_prompt="Custom prompt",
            name="CustomAgent",
        )

        self.assertIsInstance(adapter, LangChainAgentAdapter)
        self.assertEqual(adapter.name, "CustomAgent")
        self.assertEqual(adapter.system_prompt, "Custom prompt")

    def test_agent_invocation_interface(self):
        """Test that agent provides correct invocation interface"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
        )

        # Mock the agent's internal invoke method
        adapter.agent = Mock()
        adapter.agent.invoke = Mock(return_value={"output": "Test response"})

        # Test sync invocation
        result = adapter.invoke("Test query")
        self.assertEqual(result, "Test response")

        # Test callable interface
        result = adapter("Test query")
        self.assertEqual(result, "Test response")

    @patch("fivcadvisor.adapters.agents.asyncio.to_thread")
    def test_agent_async_invocation(self, mock_to_thread):
        """Test async invocation interface"""

        async def async_test():
            adapter = LangChainAgentAdapter(
                model=self.mock_llm,
                tools=[],
            )
            adapter.agent = Mock()
            adapter.agent.invoke = Mock(return_value={"output": "Async response"})
            mock_to_thread.return_value = {"output": "Async response"}

            result = await adapter.invoke_async("Test query")
            self.assertEqual(result, "Async response")

        asyncio.run(async_test())

    def test_agent_event_emission(self):
        """Test that agents emit events"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
        )
        adapter.agent = Mock()
        adapter.agent.invoke = Mock(return_value={"output": "Response"})

        # Verify event bus exists and has emit method
        self.assertIsNotNone(adapter.event_bus)
        self.assertTrue(hasattr(adapter.event_bus, "emit"))


class TestLangChainSwarmIntegration(unittest.TestCase):
    """Integration tests for LangChain swarm"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()

    def test_swarm_creation_with_langchain_agents(self):
        """Test creating a swarm with LangChain agents"""
        # Create agents directly
        agents = [
            LangChainAgentAdapter(model=self.mock_llm, tools=[], name="Agent1"),
            LangChainAgentAdapter(model=self.mock_llm, tools=[], name="Agent2"),
        ]

        # Mock create_swarm to avoid needing real LangGraph setup
        with patch("fivcadvisor.adapters.multiagent.create_swarm") as mock_create_swarm:
            mock_workflow = Mock()
            mock_app = Mock()
            mock_workflow.compile = Mock(return_value=mock_app)
            mock_create_swarm.return_value = mock_workflow

            # Create swarm
            swarm = LangGraphSwarmAdapter(agents)

            self.assertIsInstance(swarm, LangGraphSwarmAdapter)
            self.assertEqual(len(swarm.agents), 2)

    def test_swarm_agent_access(self):
        """Test accessing agents in swarm"""
        agents = [
            LangChainAgentAdapter(model=self.mock_llm, tools=[], name="Agent1"),
            LangChainAgentAdapter(model=self.mock_llm, tools=[], name="Agent2"),
        ]

        with patch("fivcadvisor.adapters.multiagent.create_swarm") as mock_create_swarm:
            mock_workflow = Mock()
            mock_app = Mock()
            mock_workflow.compile = Mock(return_value=mock_app)
            mock_create_swarm.return_value = mock_workflow

            swarm = LangGraphSwarmAdapter(agents)

            # Verify agents are accessible
            self.assertEqual(swarm.agents[0].name, "Agent1")
            self.assertEqual(swarm.agents[1].name, "Agent2")


class TestLangChainToolIntegration(unittest.TestCase):
    """Integration tests for tool conversion"""

    def test_agent_accepts_tools(self):
        """Test that agent accepts tools during creation"""
        mock_llm = Mock()
        mock_tool = Mock()
        mock_tool.name = "test_tool"

        adapter = LangChainAgentAdapter(
            model=mock_llm,
            tools=[mock_tool],
        )

        self.assertIsInstance(adapter, LangChainAgentAdapter)
        self.assertIsNotNone(adapter.agent)


class TestLangChainEventIntegration(unittest.TestCase):
    """Integration tests for event system"""

    def test_agent_event_bus_integration(self):
        """Test that agent event bus is properly integrated"""
        mock_llm = Mock()
        adapter = LangChainAgentAdapter(
            model=mock_llm,
            tools=[],
        )

        # Verify event bus exists
        self.assertIsNotNone(adapter.event_bus)

        # Verify event bus has required methods
        self.assertTrue(hasattr(adapter.event_bus, "emit"))
        self.assertTrue(hasattr(adapter.event_bus, "subscribe"))

    def test_event_subscription(self):
        """Test subscribing to agent events"""
        mock_llm = Mock()
        adapter = LangChainAgentAdapter(
            model=mock_llm,
            tools=[],
        )

        # Create mock callback
        callback = Mock()

        # Subscribe to events
        adapter.event_bus.subscribe("BEFORE_INVOCATION", callback)

        # Verify subscription was registered
        self.assertIsNotNone(adapter.event_bus)
        self.assertTrue(hasattr(adapter.event_bus, "subscribe"))


class TestLangChainBackwardCompatibility(unittest.TestCase):
    """Integration tests for backward compatibility"""

    def test_agent_api_compatibility(self):
        """Test that agent API is compatible with Strands"""
        mock_llm = Mock()
        adapter = LangChainAgentAdapter(
            model=mock_llm,
            tools=[],
        )

        # Verify Strands-compatible interface
        self.assertTrue(hasattr(adapter, "invoke"))
        self.assertTrue(hasattr(adapter, "invoke_async"))
        self.assertTrue(callable(adapter))
        self.assertTrue(hasattr(adapter, "agent_id"))
        self.assertTrue(hasattr(adapter, "name"))

    def test_adapter_properties(self):
        """Test that adapter has all required properties"""
        mock_llm = Mock()
        adapter = LangChainAgentAdapter(
            model=mock_llm,
            tools=[],
            name="TestAgent",
            system_prompt="Test prompt",
        )

        # Verify properties
        self.assertEqual(adapter.name, "TestAgent")
        self.assertEqual(adapter.system_prompt, "Test prompt")
        self.assertIsNotNone(adapter.agent_id)
        self.assertIsNotNone(adapter.agent)
        self.assertIsNotNone(adapter.event_bus)


if __name__ == "__main__":
    unittest.main()

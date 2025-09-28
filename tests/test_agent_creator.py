#!/usr/bin/env python3
"""
Tests for the agent_creator decorator and related functionality.
"""

import pytest
from unittest.mock import Mock

from fivcadvisor.agents.types import (
    AgentsRetriever,
    AgentsCreatorBase,
    FunctionAgentCreator,
    agent_creator,
)
from strands.agent import Agent


class TestFunctionAgentCreator:
    """Test the FunctionAgentCreator class."""

    def test_init(self):
        """Test FunctionAgentCreator initialization."""

        def dummy_func():
            """Test function docstring"""
            return Mock(spec=Agent)

        creator = FunctionAgentCreator("TestAgent", dummy_func)

        assert creator.name == "TestAgent"
        assert creator.description == "Test function docstring"
        assert creator._func == dummy_func

    def test_call(self):
        """Test FunctionAgentCreator call functionality."""
        mock_agent = Mock(spec=Agent)

        def create_agent(*args, **kwargs):
            """Create agent function"""
            return mock_agent

        creator = FunctionAgentCreator("TestAgent", create_agent)
        result = creator()

        assert result == mock_agent

    def test_call_with_args(self):
        """Test FunctionAgentCreator call with arguments."""
        mock_agent = Mock(spec=Agent)

        def create_agent(*args, **kwargs):
            """Create agent with args"""
            # Verify arguments are passed through
            assert args == (1, 2, 3)
            assert kwargs == {"name": "test", "model": "gpt-4"}
            return mock_agent

        creator = FunctionAgentCreator("TestAgent", create_agent)
        result = creator(1, 2, 3, name="test", model="gpt-4")

        assert result == mock_agent


class TestAgentCreatorDecorator:
    """Test the agent_creator decorator."""

    def test_decorator_basic(self):
        """Test basic decorator functionality."""

        @agent_creator("TestAgent", "A test agent creator")
        def create_test_agent():
            """Test agent creator function"""
            return Mock(spec=Agent)

        # The decorator should return a FunctionAgentCreator instance
        assert isinstance(create_test_agent, FunctionAgentCreator)
        assert create_test_agent.name == "TestAgent"
        # Description comes from function docstring, not decorator parameter
        assert create_test_agent.description == "Test agent creator function"

    def test_decorator_with_function_args(self):
        """Test decorator with function that takes arguments."""

        @agent_creator("ConfigurableAgent", "An agent that can be configured")
        def create_configurable_agent(*args, **kwargs):
            mock_agent = Mock(spec=Agent)
            mock_agent.name = kwargs.get("name", "DefaultName")
            return mock_agent

        # Test the wrapped function
        agent = create_configurable_agent(name="CustomName")
        assert agent.name == "CustomName"

    def test_decorator_preserves_functionality(self):
        """Test that the decorator preserves the original function's behavior."""
        call_count = 0

        @agent_creator("CountingAgent", "An agent that counts calls")
        def create_counting_agent():
            nonlocal call_count
            call_count += 1
            return Mock(spec=Agent)

        # Call the decorated function multiple times
        create_counting_agent()
        create_counting_agent()

        assert call_count == 2


class TestAgentsRetrieverIntegration:
    """Test integration with AgentsRetriever."""

    def test_add_decorated_creator(self):
        """Test adding a decorated creator to the retriever."""

        @agent_creator("IntegrationAgent", "An agent for integration testing")
        def create_integration_agent():
            """An agent for integration testing"""
            return Mock(spec=Agent)

        retriever = AgentsRetriever()
        retriever.add(create_integration_agent)

        # Verify it was added correctly
        assert len(retriever.get_all()) == 1
        retrieved = retriever.get("IntegrationAgent")
        assert retrieved == create_integration_agent
        assert retrieved.name == "IntegrationAgent"
        assert retrieved.description == "An agent for integration testing"

    def test_multiple_decorated_creators(self):
        """Test adding multiple decorated creators."""

        @agent_creator("Agent1", "First agent")
        def create_agent1():
            return Mock(spec=Agent)

        @agent_creator("Agent2", "Second agent")
        def create_agent2():
            return Mock(spec=Agent)

        retriever = AgentsRetriever()
        retriever.add_batch([create_agent1, create_agent2])

        assert len(retriever.get_all()) == 2
        assert retriever.get("Agent1") == create_agent1
        assert retriever.get("Agent2") == create_agent2

    def test_retrieve_and_use_creator(self):
        """Test retrieving and using a creator from the retriever."""

        @agent_creator("UsableAgent", "An agent that can be used")
        def create_usable_agent(name="DefaultName"):
            mock_agent = Mock(spec=Agent)
            mock_agent.name = name
            return mock_agent

        retriever = AgentsRetriever()
        retriever.add(create_usable_agent)

        # Retrieve and use the creator
        creator = retriever.get("UsableAgent")
        agent = creator(name="TestName")

        assert agent.name == "TestName"

    def test_duplicate_name_error(self):
        """Test that adding creators with duplicate names raises an error."""

        @agent_creator("DuplicateAgent", "First agent")
        def create_agent1():
            return Mock(spec=Agent)

        @agent_creator("DuplicateAgent", "Second agent with same name")
        def create_agent2():
            return Mock(spec=Agent)

        retriever = AgentsRetriever()
        retriever.add(create_agent1)

        # Adding a second creator with the same name should raise an error
        with pytest.raises(
            RuntimeError, match="Agent creator DuplicateAgent already exists"
        ):
            retriever.add(create_agent2)


class TestAgentsCreatorBase:
    """Test the AgentsCreatorBase abstract class."""

    def test_abstract_class(self):
        """Test that AgentsCreatorBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AgentsCreatorBase("test", "test description")

    def test_subclass_implementation(self):
        """Test that subclasses must implement __call__."""

        class IncompleteCreator(AgentsCreatorBase):
            pass

        with pytest.raises(TypeError):
            IncompleteCreator("test", "test description")

    def test_complete_subclass(self):
        """Test a complete subclass implementation."""

        class CompleteCreator(AgentsCreatorBase):
            def __init__(self, name, description):
                self._name = name
                self._description = description

            @property
            def name(self):
                return self._name

            @property
            def description(self):
                return self._description

            def __call__(self, *args, **kwargs):
                return Mock(spec=Agent)

        creator = CompleteCreator("test", "test description")
        assert creator.name == "test"
        assert creator.description == "test description"

        agent = creator()
        assert isinstance(agent, Mock)


if __name__ == "__main__":
    pytest.main([__file__])

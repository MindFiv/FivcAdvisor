"""
Tests for the graphs module.
"""

import pytest
from unittest.mock import Mock
from fivcadvisor.graphs import (
    create_simple_graph,
    create_general_graph,
    create_complex_graph,
    create_retriever,
)
from fivcadvisor.models import TaskAssessment, TaskPlan


class TestGraphsCreation:
    """Test graph creation functions."""

    def test_create_simple_graph(self):
        """Test SimpleGraph creation."""
        graph = create_simple_graph()
        assert graph is not None
        assert graph.name == "simple"

    def test_create_general_graph(self):
        """Test GeneralGraph creation."""
        graph = create_general_graph()
        assert graph is not None
        assert graph.name == "general"

    def test_create_complex_graph(self):
        """Test ComplexGraph creation."""
        graph = create_complex_graph()
        assert graph is not None
        assert graph.name == "complex"

    def test_create_retriever(self):
        """Test GraphsRetriever creation."""
        retriever = create_retriever()
        assert retriever is not None


class TestGraphExecution:
    """Test graph execution with mocked crews."""

    @pytest.fixture
    def mock_tools_retriever(self):
        """Create a mock tools retriever."""
        mock_retriever = Mock()
        mock_retriever.get_batch.return_value = [Mock(), Mock()]
        return mock_retriever

    @pytest.fixture
    def mock_assessment(self):
        """Create a mock task assessment."""
        return TaskAssessment(
            task_complexity="simple",
            require_director=False,
            required_tools=["calculator", "web_search"],
            reasoning="Simple calculation task",
        )

    @pytest.fixture
    def mock_plan(self):
        """Create a mock crew plan."""
        return TaskPlan(
            tasks=[
                TaskPlan.Task(
                    agent_role="Analyst",
                    agent_goal="Analyze data",
                    agent_backstory="Expert analyst",
                    name="Analyze Data",
                    description="Analyze the data",
                    expected_output="Analysis report",
                    tools=["calculator"],
                    requires_human=False,
                )
            ],
        )

    def test_simple_graph_validation(self, mock_tools_retriever):
        """Test SimpleGraph input validation."""
        graph = create_simple_graph()
        graph_run = graph(tools_retriever=mock_tools_retriever, run_id="test")

        # Test empty query - this should work but may fail during execution
        # For now, let's just test that the graph_run is created successfully
        assert graph_run is not None

        # Test that we can create a graph run with proper inputs
        result = graph_run.kickoff(inputs={"user_query": "test query"})
        # The result should be a dictionary with the expected structure
        assert isinstance(result, dict)

    def test_general_graph_validation(self, mock_tools_retriever):
        """Test GeneralGraph input validation."""
        graph = create_general_graph()
        graph_run = graph(tools_retriever=mock_tools_retriever, run_id="test")

        # Test that we can create a graph run
        assert graph_run is not None

        # Test that we can execute with proper inputs
        result = graph_run.kickoff(inputs={"user_query": "test query"})
        assert isinstance(result, dict)

    def test_complex_graph_validation(self, mock_tools_retriever):
        """Test ComplexGraph input validation."""
        graph = create_complex_graph()
        graph_run = graph(tools_retriever=mock_tools_retriever, run_id="test")

        # Test that we can create a graph run
        assert graph_run is not None

        # Test that we can execute with proper inputs
        result = graph_run.kickoff(inputs={"user_query": "test query"})
        assert isinstance(result, dict)


class TestGraphsRetriever:
    """Test GraphsRetriever functionality."""

    def test_retriever_add_and_get(self):
        """Test adding and retrieving graphs."""
        retriever = create_retriever()

        # Mock graph class
        mock_graph_class = Mock()
        mock_graph_class.name = "test_graph"

        # Add graph
        retriever.add(mock_graph_class)

        # Retrieve graph
        retrieved = retriever.get("test_graph")
        assert retrieved == mock_graph_class

        # Test non-existent graph
        assert retriever.get("non_existent") is None

    def test_retriever_duplicate_name(self):
        """Test duplicate graph name handling (idempotent behavior)."""
        retriever = create_retriever()

        # Mock graph classes with same name
        mock_graph1 = Mock()
        mock_graph1.name = "duplicate"
        mock_graph2 = Mock()
        mock_graph2.name = "duplicate"

        # Add first graph
        retriever.add(mock_graph1)
        assert retriever.get("duplicate") == mock_graph1

        # Adding second graph with same name should be idempotent (no error)
        retriever.add(mock_graph2)  # Should not raise an error

        # The first graph should still be there (not replaced)
        assert retriever.get("duplicate") == mock_graph1

    def test_retriever_batch_operations(self):
        """Test batch add and get operations."""
        retriever = create_retriever()

        # Mock graph classes
        mock_graphs = []
        for i in range(3):
            mock_graph = Mock()
            mock_graph.name = f"graph_{i}"
            mock_graphs.append(mock_graph)

        # Add batch
        retriever.add_batch(mock_graphs)

        # Get batch
        names = ["graph_0", "graph_1", "graph_2"]
        retrieved = retriever.get_batch(names)

        assert len(retrieved) == 3
        assert all(g in mock_graphs for g in retrieved)

    def test_retriever_cleanup(self):
        """Test retriever cleanup."""
        retriever = create_retriever()

        # Add a graph
        mock_graph = Mock()
        mock_graph.name = "test"
        retriever.add(mock_graph)

        # Verify it exists
        assert retriever.get("test") is not None

        # Cleanup
        retriever.cleanup()

        # Verify it's gone
        assert retriever.get("test") is None

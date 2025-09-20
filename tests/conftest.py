"""
Shared pytest fixtures and configuration for FivcAdvisor tests.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from fivcadvisor.api import create_server_app
from fivcadvisor.api.models import FlowExecuteRequest


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client():
    """Create a FastAPI test client for the server app."""
    app = create_server_app()
    return TestClient(app)


@pytest.fixture
def sample_flow_request():
    """Sample valid flow execution request."""
    return FlowExecuteRequest(user_query="Calculate 2 + 2", config={"verbose": True})


@pytest.fixture
def sample_simple_request():
    """Sample request for simple flow."""
    return FlowExecuteRequest(user_query="What is 5 * 3?", config={})


@pytest.fixture
def sample_complex_request():
    """Sample request for complex flow."""
    return FlowExecuteRequest(
        user_query="Analyze the current market trends and provide investment recommendations",
        config={"detailed": True},
    )


@pytest.fixture
def mock_flow_result():
    """Mock successful flow execution result."""
    return {
        "result": "The answer is 4",
        "status": "completed",
        "metadata": {"execution_time": 1.5, "steps_completed": 3},
    }


@pytest.fixture
def mock_assessment_result():
    """Mock task assessment result."""
    return {
        "require_director": False,
        "complexity_score": 2,
        "required_tools": ["Calculator"],
        "reasoning": "Simple mathematical calculation",
    }


@pytest.fixture
def mock_complex_assessment_result():
    """Mock complex task assessment result."""
    return {
        "require_director": True,
        "complexity_score": 8,
        "required_tools": ["WebSearcher", "DataAnalyzer", "ReportGenerator"],
        "reasoning": "Complex analysis requiring multiple specialized tools",
    }


@pytest.fixture
def mock_crew_result():
    """Mock crew execution result."""
    mock_result = Mock()
    mock_result.to_dict.return_value = {
        "result": "Task completed successfully",
        "agent_outputs": ["Step 1 completed", "Step 2 completed"],
        "final_answer": "The calculation result is 4",
    }
    return mock_result


@pytest.fixture
def mock_flow_events():
    """Mock flow execution events."""
    return [
        {"event": "flow_started", "timestamp": "2024-01-01T10:00:00Z"},
        {
            "event": "agent_thinking",
            "agent": "calculator",
            "message": "Processing calculation",
        },
        {"event": "tool_used", "tool": "Calculator", "input": "2 + 2"},
        {
            "event": "agent_response",
            "agent": "calculator",
            "response": "The result is 4",
        },
        {"event": "flow_completed", "timestamp": "2024-01-01T10:00:05Z"},
    ]


class MockFlow:
    """Mock flow class for testing."""

    def __init__(self, name: str, result: Any = None, should_error: bool = False):
        self.name = name
        self.result = result or {"result": f"Mock {name} flow result"}
        self.should_error = should_error
        self.tools_retriever = None
        self.session_id = "test-session-123"
        self.verbose = False

    async def kickoff_async(self, inputs: Dict[str, Any]) -> Any:
        """Mock async flow execution."""
        if self.should_error:
            raise Exception(f"Mock error in {self.name} flow")

        # Simulate some processing time
        await asyncio.sleep(0.1)
        return self.result


@pytest.fixture
def mock_general_flow():
    """Mock GeneralFlow class."""
    return MockFlow("general")


@pytest.fixture
def mock_simple_flow():
    """Mock SimpleFlow class."""
    return MockFlow("simple")


@pytest.fixture
def mock_complex_flow():
    """Mock ComplexFlow class."""
    return MockFlow("complex")


@pytest.fixture
def mock_error_flow():
    """Mock flow that raises an error."""
    return MockFlow("error", should_error=True)


@pytest.fixture
def mock_session():
    """Mock session for testing."""
    mock_session = Mock()
    mock_session.id = "test-session-123"
    mock_session.events = AsyncMock()
    mock_session.events.get = AsyncMock(side_effect=asyncio.TimeoutError())
    return mock_session


@pytest.fixture
def mock_session_manager():
    """Mock session manager."""
    mock_manager = Mock()
    mock_session = Mock()
    mock_session.id = "test-session-123"
    mock_session.events = Mock()
    mock_session.events.get = AsyncMock(side_effect=asyncio.TimeoutError())

    mock_manager.create_session.return_value.__enter__.return_value = mock_session
    mock_manager.create_session.return_value.__exit__.return_value = None

    return mock_manager


def collect_streaming_response(response) -> list:
    """Helper function to collect all items from a streaming response."""
    items = []
    for chunk in response.iter_lines():
        if chunk:
            items.append(chunk.decode())
    return items


def parse_streaming_json_response(response) -> list:
    """Helper function to parse streaming JSON response."""
    import json

    items = []
    for chunk in response.iter_lines():
        if chunk:
            try:
                items.append(json.loads(chunk.decode()))
            except json.JSONDecodeError:
                # Handle non-JSON chunks
                items.append(chunk.decode())
    return items

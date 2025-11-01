"""
Comprehensive tests for AgentsRunnable implementation.

Tests verify:
- AgentsRunnable initialization with various parameters
- Synchronous execution via run() method
- Asynchronous execution via run_async() method
- Tool handling and conversion
- Error handling and edge cases
- Runnable interface compliance
- Message history support (string queries and message lists)
- Structured response handling with response_model
"""

from unittest.mock import MagicMock, patch
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

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
        # Mock stream method instead of invoke
        mock_agent.stream.return_value = [
            ("values", {"messages": [AIMessage(content="Test response")]})
        ]
        mock_agent.InputType = MagicMock(return_value={"messages": []})
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
        mock_agent.stream.return_value = [
            ("values", {"messages": [AIMessage(content="Test response")]})
        ]
        mock_agent.InputType = MagicMock(return_value={"messages": []})
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


class TestAgentsRunnableStructuredResponse:
    """Test AgentsRunnable structured response handling."""

    def test_init_with_response_model(self):
        """Test initialization with response_model parameter."""

        class TestResponse(BaseModel):
            answer: str
            confidence: float

        mock_model = MagicMock(spec=BaseChatModel)

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            response_model=TestResponse,
        )

        assert agent._agent is not None

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_returns_structured_response(self, mock_create_agent):
        """Test that run() returns structured response when available."""

        class TestResponse(BaseModel):
            answer: str
            confidence: float

        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        # Mock agent returns structured_response in output
        test_response = TestResponse(answer="Test answer", confidence=0.95)
        response_message = AIMessage(content="Test answer")

        # Mock astream to return async generator
        async def mock_astream(*args, **kwargs):
            yield (
                "values",
                {"messages": [response_message], "structured_response": test_response},
            )

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            response_model=TestResponse,
        )

        result = agent.run("test query")

        assert result == test_response
        assert isinstance(result, TestResponse)
        assert result.answer == "Test answer"
        assert result.confidence == 0.95

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_async_returns_structured_response(self, mock_create_agent):
        """Test that run_async() returns structured response when available."""
        import asyncio

        class TestResponse(BaseModel):
            answer: str
            confidence: float

        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        # Mock agent returns structured_response in output
        test_response = TestResponse(answer="Async answer", confidence=0.85)
        response_message = AIMessage(content="Async answer")

        async def mock_astream(*args, **kwargs):
            yield (
                "values",
                {"messages": [response_message], "structured_response": test_response},
            )

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            response_model=TestResponse,
        )

        # Test the async call
        async def test_async():
            result = await agent.run_async("test query")
            assert result == test_response
            assert isinstance(result, TestResponse)
            assert result.answer == "Async answer"
            assert result.confidence == 0.85

        asyncio.run(test_async())

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_falls_back_to_message_without_structured_response(
        self, mock_create_agent
    ):
        """Test that run() returns BaseMessage when structured_response is not present."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        # Mock agent returns only messages, no structured_response
        async def mock_astream(*args, **kwargs):
            yield ("values", {"messages": [AIMessage(content="Plain text response")]})

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        result = agent.run("test query")

        assert isinstance(result, AIMessage)
        assert result.content == "Plain text response"

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_with_multiple_messages_returns_last_message(self, mock_create_agent):
        """Test that run() returns the last message when multiple messages are present."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        # Mock agent returns multiple messages
        async def mock_astream(*args, **kwargs):
            yield (
                "values",
                {
                    "messages": [
                        AIMessage(content="First response"),
                        AIMessage(content="Second response"),
                        AIMessage(content="Final response"),
                    ]
                },
            )

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        result = agent.run("test query")

        assert isinstance(result, AIMessage)
        assert result.content == "Final response"

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_structured_response_takes_precedence_over_messages(
        self, mock_create_agent
    ):
        """Test that structured_response takes precedence over messages."""

        class TestResponse(BaseModel):
            answer: str

        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        # Mock agent returns both structured_response and messages
        test_response = TestResponse(answer="Structured answer")

        async def mock_astream(*args, **kwargs):
            yield (
                "values",
                {
                    "structured_response": test_response,
                    "messages": [AIMessage(content="This should be ignored")],
                },
            )

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            response_model=TestResponse,
        )

        result = agent.run("test query")

        # Should return structured_response, not the message
        assert result == test_response
        assert isinstance(result, TestResponse)
        assert result.answer == "Structured answer"


class TestAgentsRunnableMessageHistory:
    """Test AgentsRunnable message history support."""

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_with_string_query(self, mock_create_agent):
        """Test that run() works with string query."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        async def mock_astream(*args, **kwargs):
            yield ("values", {"messages": [AIMessage(content="Response")]})

        mock_agent.astream = MagicMock(side_effect=mock_astream)
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        result = agent.run("test query")

        assert isinstance(result, AIMessage)
        assert result.content == "Response"

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_with_message_list(self, mock_create_agent):
        """Test that run() works with list of messages."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        async def mock_astream(*args, **kwargs):
            yield ("values", {"messages": [AIMessage(content="Response to history")]})

        mock_agent.astream = MagicMock(side_effect=mock_astream)
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        # Create message history
        messages = [
            HumanMessage(content="First question"),
            AIMessage(content="First answer"),
            HumanMessage(content="Follow-up question"),
        ]

        result = agent.run(messages)

        assert isinstance(result, AIMessage)
        assert result.content == "Response to history"

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_with_empty_message_list(self, mock_create_agent):
        """Test that run() works with empty message list."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        async def mock_astream(*args, **kwargs):
            yield ("values", {"messages": [AIMessage(content="Default response")]})

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        result = agent.run([])

        assert isinstance(result, AIMessage)
        assert result.content == "Default response"

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_with_single_message(self, mock_create_agent):
        """Test that run() works with single message in list."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        async def mock_astream(*args, **kwargs):
            yield (
                "values",
                {"messages": [AIMessage(content="Single message response")]},
            )

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        messages = [HumanMessage(content="Single question")]
        result = agent.run(messages)

        assert isinstance(result, AIMessage)
        assert result.content == "Single message response"

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_async_with_string_query(self, mock_create_agent):
        """Test that run_async() works with string query."""
        import asyncio

        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        async def mock_astream(*args, **kwargs):
            yield ("values", {"messages": [AIMessage(content="Async response")]})

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        async def test_async():
            result = await agent.run_async("test query")
            assert isinstance(result, AIMessage)
            assert result.content == "Async response"

        asyncio.run(test_async())

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_async_with_message_list(self, mock_create_agent):
        """Test that run_async() works with list of messages."""
        import asyncio

        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        async def mock_astream(*args, **kwargs):
            yield (
                "values",
                {"messages": [AIMessage(content="Async history response")]},
            )

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        async def test_async():
            messages = [
                HumanMessage(content="First question"),
                AIMessage(content="First answer"),
                HumanMessage(content="Follow-up question"),
            ]
            result = await agent.run_async(messages)
            assert isinstance(result, AIMessage)
            assert result.content == "Async history response"

        asyncio.run(test_async())

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_with_message_list_and_structured_response(self, mock_create_agent):
        """Test that run() with message list returns structured response when available."""

        class TestResponse(BaseModel):
            answer: str
            confidence: float

        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        test_response = TestResponse(answer="Structured answer", confidence=0.9)
        response_message = AIMessage(content="Structured answer")

        async def mock_astream(*args, **kwargs):
            yield (
                "values",
                {"messages": [response_message], "structured_response": test_response},
            )

        mock_agent.astream = MagicMock(side_effect=mock_astream)
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            response_model=TestResponse,
        )

        messages = [
            HumanMessage(content="Question 1"),
            AIMessage(content="Answer 1"),
            HumanMessage(content="Question 2"),
        ]

        result = agent.run(messages)

        assert result == test_response
        assert isinstance(result, TestResponse)
        assert result.answer == "Structured answer"

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_async_with_message_list_and_structured_response(
        self, mock_create_agent
    ):
        """Test that run_async() with message list returns structured response when available."""
        import asyncio

        class TestResponse(BaseModel):
            answer: str
            confidence: float

        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        test_response = TestResponse(answer="Async structured answer", confidence=0.85)
        response_message = AIMessage(content="Async structured answer")

        async def mock_astream(*args, **kwargs):
            yield (
                "values",
                {"messages": [response_message], "structured_response": test_response},
            )

        mock_agent.astream = mock_astream
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
            response_model=TestResponse,
        )

        async def test_async():
            messages = [
                HumanMessage(content="Question 1"),
                AIMessage(content="Answer 1"),
                HumanMessage(content="Question 2"),
            ]
            result = await agent.run_async(messages)
            assert result == test_response
            assert isinstance(result, TestResponse)

        asyncio.run(test_async())

    @patch("fivcadvisor.agents.types.runnables.create_agent")
    def test_run_with_mixed_message_types(self, mock_create_agent):
        """Test that run() works with mixed message types in history."""
        mock_model = MagicMock(spec=BaseChatModel)
        mock_agent = MagicMock()

        async def mock_astream(*args, **kwargs):
            yield ("values", {"messages": [AIMessage(content="Mixed response")]})

        mock_agent.astream = MagicMock(side_effect=mock_astream)
        mock_agent.InputType = MagicMock(return_value={"messages": []})
        mock_create_agent.return_value = mock_agent

        agent = AgentsRunnable(
            model=mock_model,
            tools=[],
            agent_name="TestAgent",
        )

        # Create message history with different message types
        messages = [
            HumanMessage(content="User question 1"),
            AIMessage(content="Assistant answer 1"),
            HumanMessage(content="User question 2"),
            AIMessage(content="Assistant answer 2"),
            HumanMessage(content="User question 3"),
        ]

        result = agent.run(messages)

        assert isinstance(result, AIMessage)
        assert result.content == "Mixed response"


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

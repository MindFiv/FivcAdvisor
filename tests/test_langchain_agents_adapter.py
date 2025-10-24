"""
Tests for LangChain Agent Adapter

Tests the LangChainAgentAdapter and create_langchain_agent factory function
to ensure they provide a Strands-compatible API while using LangChain under the hood.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import Tool

from fivcadvisor.adapters.agents import (
    LangChainAgentAdapter,
    create_langchain_agent,
)


class TestLangChainAgentAdapter(unittest.TestCase):
    """Test LangChainAgentAdapter class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock LLM with bind_tools support
        self.mock_llm = MagicMock(spec=BaseLanguageModel)
        self.mock_llm.bind_tools = MagicMock(return_value=self.mock_llm)

        # Create mock tools
        self.mock_tool = Mock(spec=Tool)
        self.mock_tool.name = "test_tool"
        self.mock_tool.description = "A test tool"
        self.mock_tools = [self.mock_tool]

    def test_adapter_initialization(self):
        """Test adapter initialization with required parameters"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
            system_prompt="You are a test agent",
            name="TestAgent",
        )

        self.assertEqual(adapter.name, "TestAgent")
        self.assertEqual(adapter.system_prompt, "You are a test agent")
        self.assertIsNotNone(adapter.agent_id)
        self.assertEqual(adapter.model, self.mock_llm)
        self.assertEqual(adapter.tools, self.mock_tools)

    def test_adapter_with_custom_agent_id(self):
        """Test adapter with custom agent ID"""
        custom_id = "custom-agent-123"
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
            agent_id=custom_id,
        )

        self.assertEqual(adapter.agent_id, custom_id)

    def test_adapter_with_callback_handler(self):
        """Test adapter with callback handler"""
        callback = Mock()
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
            callback_handler=callback,
        )

        self.assertEqual(adapter.callback_handler, callback)

    def test_adapter_with_conversation_manager(self):
        """Test adapter with conversation manager"""
        conv_mgr = Mock()
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
            conversation_manager=conv_mgr,
        )

        self.assertEqual(adapter.conversation_manager, conv_mgr)

    def test_adapter_with_hooks(self):
        """Test adapter with hooks"""
        hook1 = Mock()
        hook2 = Mock()
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
            hooks=[hook1, hook2],
        )

        self.assertEqual(len(adapter.hooks), 2)
        self.assertIn(hook1, adapter.hooks)
        self.assertIn(hook2, adapter.hooks)

    def test_adapter_callable(self):
        """Test that adapter is callable"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
        )

        # Mock the agent
        adapter.agent = Mock()
        adapter.agent.invoke = Mock(return_value={"output": "Test response"})

        result = adapter("Test query")
        self.assertEqual(result, "Test response")

    @patch("fivcadvisor.adapters.agents.asyncio.to_thread")
    def test_invoke_async(self, mock_to_thread):
        """Test async invocation"""

        async def async_test():
            adapter = LangChainAgentAdapter(
                model=self.mock_llm,
                tools=self.mock_tools,
            )

            # Mock the agent
            adapter.agent = Mock()
            adapter.agent.invoke = Mock(return_value={"output": "Async response"})
            mock_to_thread.return_value = {"output": "Async response"}

            result = await adapter.invoke_async("Test query")
            self.assertEqual(result, "Async response")

        asyncio.run(async_test())

    def test_invoke_sync(self):
        """Test synchronous invocation"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
        )

        # Mock the agent
        adapter.agent = Mock()
        adapter.agent.invoke = Mock(return_value={"output": "Sync response"})

        result = adapter.invoke("Test query")
        self.assertEqual(result, "Sync response")

    def test_invoke_with_callback(self):
        """Test invocation with callback handler"""
        callback = Mock()
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
            callback_handler=callback,
        )

        # Mock the agent
        adapter.agent = Mock()
        adapter.agent.invoke = Mock(return_value={"output": "Response"})

        _ = adapter.invoke("Test query")

        # Verify callback was called
        callback.assert_called_once()
        call_kwargs = callback.call_args[1]
        # New format: callback is called with result parameter containing message and output
        self.assertIn("result", call_kwargs)
        result_dict = call_kwargs["result"]
        self.assertEqual(result_dict["output"], "Response")
        self.assertIn("message", result_dict)


class TestCreateLangChainAgent(unittest.TestCase):
    """Test create_langchain_agent factory function"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = MagicMock(spec=BaseLanguageModel)
        self.mock_llm.bind_tools = MagicMock(return_value=self.mock_llm)
        self.mock_tool = Mock(spec=Tool)
        self.mock_tool.name = "test_tool"
        self.mock_tools = [self.mock_tool]

    def test_create_agent_basic(self):
        """Test basic agent creation"""
        agent = create_langchain_agent(
            model=self.mock_llm,
            tools=self.mock_tools,
        )

        self.assertIsInstance(agent, LangChainAgentAdapter)
        self.assertEqual(agent.model, self.mock_llm)

    def test_create_agent_with_system_prompt(self):
        """Test agent creation with system prompt"""
        prompt = "You are a helpful assistant"
        agent = create_langchain_agent(
            model=self.mock_llm,
            tools=self.mock_tools,
            system_prompt=prompt,
        )

        self.assertEqual(agent.system_prompt, prompt)

    def test_create_agent_with_name(self):
        """Test agent creation with custom name"""
        agent = create_langchain_agent(
            model=self.mock_llm,
            tools=self.mock_tools,
            name="CustomAgent",
        )

        self.assertEqual(agent.name, "CustomAgent")

    def test_create_agent_with_agent_id(self):
        """Test agent creation with custom agent ID"""
        agent_id = "agent-123"
        agent = create_langchain_agent(
            model=self.mock_llm,
            tools=self.mock_tools,
            agent_id=agent_id,
        )

        self.assertEqual(agent.agent_id, agent_id)

    def test_create_agent_with_callback(self):
        """Test agent creation with callback handler"""
        callback = Mock()
        agent = create_langchain_agent(
            model=self.mock_llm,
            tools=self.mock_tools,
            callback_handler=callback,
        )

        self.assertEqual(agent.callback_handler, callback)

    def test_create_agent_without_tools(self):
        """Test agent creation without tools"""
        agent = create_langchain_agent(
            model=self.mock_llm,
        )

        self.assertIsInstance(agent, LangChainAgentAdapter)
        self.assertEqual(len(agent.tools), 0)

    def test_create_agent_with_strands_tools(self):
        """Test agent creation with Strands-style tools"""
        # Create mock Strands tool
        strands_tool = Mock()
        strands_tool.tool_name = "strands_tool"
        strands_tool.tool_spec = {"description": "A Strands tool"}
        strands_tool.func = lambda x: x * 2

        with patch(
            "fivcadvisor.adapters.agents.convert_strands_tools_to_langchain"
        ) as mock_convert:
            mock_convert.return_value = [self.mock_tool]

            agent = create_langchain_agent(
                model=self.mock_llm,
                tools=[strands_tool],
            )

            # Verify conversion was called
            mock_convert.assert_called_once()
            self.assertIsInstance(agent, LangChainAgentAdapter)


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agent creation and usage"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = MagicMock(spec=BaseLanguageModel)
        self.mock_llm.bind_tools = MagicMock(return_value=self.mock_llm)
        self.mock_tool = Mock(spec=Tool)
        self.mock_tool.name = "test_tool"
        self.mock_tools = [self.mock_tool]

    def test_agent_properties(self):
        """Test agent properties are accessible"""
        agent = create_langchain_agent(
            model=self.mock_llm,
            tools=self.mock_tools,
            name="TestAgent",
            system_prompt="Test prompt",
        )

        # Verify all properties are accessible
        self.assertIsNotNone(agent.agent_id)
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.system_prompt, "Test prompt")
        self.assertEqual(agent.model, self.mock_llm)
        self.assertEqual(agent.tools, self.mock_tools)
        self.assertIsNotNone(agent.agent)
        self.assertIsNotNone(agent.event_bus)

    def test_agent_with_all_parameters(self):
        """Test agent creation with all parameters"""
        callback = Mock()
        conv_mgr = Mock()
        hook = Mock()

        agent = create_langchain_agent(
            model=self.mock_llm,
            tools=self.mock_tools,
            system_prompt="Full test",
            name="FullAgent",
            agent_id="full-123",
            callback_handler=callback,
            conversation_manager=conv_mgr,
            hooks=[hook],
        )

        self.assertEqual(agent.agent_id, "full-123")
        self.assertEqual(agent.name, "FullAgent")
        self.assertEqual(agent.system_prompt, "Full test")
        self.assertEqual(agent.callback_handler, callback)
        self.assertEqual(agent.conversation_manager, conv_mgr)
        self.assertEqual(len(agent.hooks), 1)

    @patch("fivcadvisor.adapters.agents.asyncio.to_thread")
    def test_structured_output_async(self, mock_to_thread):
        """Test structured output async method"""
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            name: str
            value: int

        async def async_test():
            agent = create_langchain_agent(
                model=self.mock_llm,
                tools=self.mock_tools,
            )
            agent.agent = Mock()
            agent.agent.invoke = Mock(
                return_value={"output": '{"name": "test", "value": 42}'}
            )
            mock_to_thread.return_value = {"output": '{"name": "test", "value": 42}'}

            result = await agent.structured_output_async(
                TestSchema, prompt="Test prompt"
            )
            self.assertEqual(result.name, "test")
            self.assertEqual(result.value, 42)

        asyncio.run(async_test())

    @patch("fivcadvisor.adapters.agents.asyncio.to_thread")
    def test_structured_output_async_with_extra_text(self, mock_to_thread):
        """Test structured output async with extra text in response"""
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            name: str
            value: int

        async def async_test():
            agent = create_langchain_agent(
                model=self.mock_llm,
                tools=self.mock_tools,
            )
            agent.agent = Mock()
            # Response with extra text before and after JSON
            response_text = 'Here is the result: {"name": "test", "value": 42} Done!'
            agent.agent.invoke = Mock(return_value={"output": response_text})
            mock_to_thread.return_value = {"output": response_text}

            result = await agent.structured_output_async(
                TestSchema, prompt="Test prompt"
            )
            self.assertEqual(result.name, "test")
            self.assertEqual(result.value, 42)

        asyncio.run(async_test())

    @patch("fivcadvisor.adapters.agents.asyncio.to_thread")
    def test_message_added_event_emission(self, mock_to_thread):
        """Test that MESSAGE_ADDED events are emitted during invocation"""

        async def async_test():
            agent = create_langchain_agent(
                model=self.mock_llm,
                tools=self.mock_tools,
            )
            agent.agent = Mock()
            agent.agent.invoke = Mock(return_value={"output": "Test response"})
            mock_to_thread.return_value = {"output": "Test response"}

            # Get event history before invocation
            events_before = len(agent.event_bus.get_history())

            # Invoke agent
            _ = await agent.invoke_async("Test query")

            # Get event history after invocation
            events_after = agent.event_bus.get_history()

            # Verify events were emitted
            self.assertGreater(len(events_after), events_before)

            # Check for MESSAGE_ADDED event
            from fivcadvisor.adapters.events import EventType

            message_events = [
                e for e in events_after if e.event_type == EventType.MESSAGE_ADDED
            ]
            self.assertGreater(len(message_events), 0)

            # Verify the message event contains the response
            message_event = message_events[0]
            self.assertEqual(message_event.message, "Test response")
            self.assertEqual(message_event.role, "assistant")

        asyncio.run(async_test())

    @patch("fivcadvisor.adapters.agents.asyncio.to_thread")
    def test_callback_receives_message_object(self, mock_to_thread):
        """Test that callback handler receives Message object in result"""

        async def async_test():
            callback = Mock()
            agent = create_langchain_agent(
                model=self.mock_llm,
                tools=self.mock_tools,
                callback_handler=callback,
            )
            agent.agent = Mock()
            agent.agent.invoke = Mock(return_value={"output": "Test response"})
            mock_to_thread.return_value = {"output": "Test response"}

            # Invoke agent
            _ = await agent.invoke_async("Test query")

            # Verify callback was called
            callback.assert_called_once()
            call_kwargs = callback.call_args[1]

            # Verify result parameter contains message and output
            self.assertIn("result", call_kwargs)
            result_dict = call_kwargs["result"]
            self.assertIn("message", result_dict)
            self.assertIn("output", result_dict)

            # Verify message is a proper Message object
            message = result_dict["message"]
            self.assertEqual(message["role"], "assistant")
            self.assertIn("content", message)
            self.assertEqual(len(message["content"]), 1)
            self.assertEqual(message["content"][0]["text"], "Test response")

        asyncio.run(async_test())


class TestEventSystemIntegration(unittest.TestCase):
    """Integration tests for event system and message persistence"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = MagicMock(spec=BaseLanguageModel)
        self.mock_llm.bind_tools = MagicMock(return_value=self.mock_llm)
        self.mock_tool = Mock(spec=Tool)
        self.mock_tool.name = "test_tool"
        self.mock_tools = [self.mock_tool]

    @patch("fivcadvisor.adapters.agents.asyncio.to_thread")
    def test_complete_event_flow(self, mock_to_thread):
        """Test complete event flow from invocation to completion"""

        async def async_test():
            from fivcadvisor.adapters.events import EventType

            # Create agent with callback
            callback = Mock()
            agent = create_langchain_agent(
                model=self.mock_llm,
                tools=self.mock_tools,
                callback_handler=callback,
            )
            agent.agent = Mock()
            agent.agent.invoke = Mock(return_value={"output": "Complete response"})
            mock_to_thread.return_value = {"output": "Complete response"}

            # Clear event history
            agent.event_bus.clear_history()

            # Invoke agent
            _ = await agent.invoke_async("Test query")

            # Get all events
            events = agent.event_bus.get_history()

            # Verify event sequence
            event_types = [e.event_type for e in events]
            self.assertIn(EventType.BEFORE_INVOCATION, event_types)
            self.assertIn(EventType.MESSAGE_ADDED, event_types)
            self.assertIn(EventType.AFTER_INVOCATION, event_types)

            # Verify order
            before_idx = event_types.index(EventType.BEFORE_INVOCATION)
            message_idx = event_types.index(EventType.MESSAGE_ADDED)
            after_idx = event_types.index(EventType.AFTER_INVOCATION)
            self.assertLess(before_idx, message_idx)
            self.assertLess(message_idx, after_idx)

            # Verify callback was called with result
            callback.assert_called_once()
            call_kwargs = callback.call_args[1]
            self.assertIn("result", call_kwargs)
            result_dict = call_kwargs["result"]
            self.assertEqual(result_dict["output"], "Complete response")
            self.assertIn("message", result_dict)

        asyncio.run(async_test())

    @patch("fivcadvisor.adapters.agents.asyncio.to_thread")
    def test_message_persistence_through_callback(self, mock_to_thread):
        """Test that messages are properly persisted through callback"""

        async def async_test():
            from fivcadvisor.agents.types.monitors import AgentsMonitor
            from fivcadvisor.agents.types.repositories.files import (
                FileAgentsRuntimeRepository,
            )
            from fivcadvisor.agents.types import AgentsRuntime
            from fivcadvisor.utils import OutputDir
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                # Create repository and runtime
                repo = FileAgentsRuntimeRepository(output_dir=OutputDir(tmpdir))
                runtime = AgentsRuntime(agent_id="test-agent", agent_name="TestAgent")

                # Create monitor as callback
                monitor = AgentsMonitor(runtime=runtime, runtime_repo=repo)

                # Create agent with monitor as callback
                agent = create_langchain_agent(
                    model=self.mock_llm,
                    tools=self.mock_tools,
                    callback_handler=monitor,
                    agent_id="test-agent",
                    name="TestAgent",
                )
                agent.agent = Mock()
                agent.agent.invoke = Mock(return_value={"output": "Persisted response"})
                mock_to_thread.return_value = {"output": "Persisted response"}

                # Invoke agent
                _ = await agent.invoke_async("Test query")

                # Verify runtime was updated with message
                self.assertIsNotNone(runtime.reply)
                self.assertEqual(runtime.reply["role"], "assistant")
                self.assertEqual(len(runtime.reply["content"]), 1)
                self.assertEqual(
                    runtime.reply["content"][0]["text"], "Persisted response"
                )

        asyncio.run(async_test())


class TestToolCalling(unittest.TestCase):
    """Test tool calling functionality in SimpleAgent"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = MagicMock(spec=BaseLanguageModel)

        # Create a mock tool
        self.mock_tool = Mock(spec=Tool)
        self.mock_tool.name = "calculator"
        self.mock_tool.description = "A calculator tool"
        self.mock_tool.invoke = Mock(return_value=4)

        self.mock_tools = [self.mock_tool]

    def test_simple_agent_with_tool_calls(self):
        """Test that SimpleAgent properly handles tool calls"""
        # Mock the LLM to return a response with tool calls
        mock_response = Mock()
        mock_response.tool_calls = [
            {"name": "calculator", "args": {"expression": "2+2"}}
        ]
        mock_response.content = ""

        # Mock bind_tools to return a mock LLM that returns our response
        mock_llm_with_tools = Mock()
        mock_llm_with_tools.invoke = Mock(return_value=mock_response)
        self.mock_llm.bind_tools = Mock(return_value=mock_llm_with_tools)

        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
            system_prompt="You are a helpful assistant",
        )

        # Invoke the agent
        result = adapter.invoke("What is 2+2?")

        # Verify the tool was called
        self.mock_tool.invoke.assert_called_once()

        # Verify the result contains tool results (result is a string)
        self.assertIsInstance(result, str)
        self.assertIn("calculator", result)

    def test_simple_agent_without_tools(self):
        """Test that SimpleAgent works without tools"""
        # Mock the LLM to return a simple response
        mock_response = Mock()
        mock_response.content = "Hello, I'm an assistant"
        mock_response.tool_calls = None

        self.mock_llm.invoke = Mock(return_value=mock_response)

        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
            system_prompt="You are a helpful assistant",
        )

        # Invoke the agent
        result = adapter.invoke("Hello")

        # Verify the result (result is a string)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Hello, I'm an assistant")

    def test_simple_agent_tool_error_handling(self):
        """Test that SimpleAgent handles tool errors gracefully"""
        # Mock the tool to raise an error
        self.mock_tool.invoke = Mock(side_effect=Exception("Tool error"))

        # Mock the LLM to return a response with tool calls
        mock_response = Mock()
        mock_response.tool_calls = [
            {"name": "calculator", "args": {"expression": "invalid"}}
        ]
        mock_response.content = ""

        # Mock bind_tools
        mock_llm_with_tools = Mock()
        mock_llm_with_tools.invoke = Mock(return_value=mock_response)
        self.mock_llm.bind_tools = Mock(return_value=mock_llm_with_tools)

        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=self.mock_tools,
            system_prompt="You are a helpful assistant",
        )

        # Invoke the agent
        result = adapter.invoke("What is 2+2?")

        # Verify the result contains error information (result is a string)
        self.assertIsInstance(result, str)
        self.assertIn("error", result.lower())


if __name__ == "__main__":
    unittest.main()

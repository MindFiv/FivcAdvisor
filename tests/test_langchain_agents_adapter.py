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
        # Create mock LLM
        self.mock_llm = Mock(spec=BaseLanguageModel)

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

        result = adapter.invoke("Test query")

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
        self.mock_llm = Mock(spec=BaseLanguageModel)
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
        self.mock_llm = Mock(spec=BaseLanguageModel)
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


if __name__ == "__main__":
    unittest.main()

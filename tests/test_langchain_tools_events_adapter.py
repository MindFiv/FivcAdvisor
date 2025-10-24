"""
Tests for LangChain tools and events adapters.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from fivcadvisor.adapters import (
    # Tools
    convert_strands_tool_to_langchain,
    convert_strands_tools_to_langchain,
    create_tool_adapter,
    is_strands_tool,
    is_langchain_tool,
    ToolAdapter,
    adapt_tool,
    adapt_tools,
    # Events
    EventType,
    Event,
    AgentInitializedEvent,
    BeforeInvocationEvent,
    AfterInvocationEvent,
    MessageAddedEvent,
    ToolCalledEvent,
    ToolResultEvent,
    ErrorOccurredEvent,
    EventBus,
    get_event_bus,
    emit_event,
    subscribe_to_event,
)


class TestToolsAdapter(unittest.TestCase):
    """Test cases for tools adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock Strands tool
        self.mock_strands_tool = Mock()
        self.mock_strands_tool.tool_name = "test_tool"
        self.mock_strands_tool.tool_spec = {
            "description": "A test tool"
        }
        self.mock_strands_tool.func = lambda x: x * 2
    
    def test_is_strands_tool(self):
        """Test is_strands_tool function."""
        self.assertTrue(is_strands_tool(self.mock_strands_tool))
        self.assertFalse(is_strands_tool("not a tool"))
        self.assertFalse(is_strands_tool(None))
    
    def test_convert_strands_tool_to_langchain(self):
        """Test converting Strands tool to LangChain tool."""
        langchain_tool = convert_strands_tool_to_langchain(self.mock_strands_tool)
        self.assertIsNotNone(langchain_tool)
        self.assertEqual(langchain_tool.name, "test_tool")
        self.assertEqual(langchain_tool.description, "A test tool")
    
    def test_convert_strands_tools_to_langchain(self):
        """Test converting multiple Strands tools to LangChain tools."""
        mock_tool2 = Mock()
        mock_tool2.tool_name = "test_tool2"
        mock_tool2.tool_spec = {"description": "Another test tool"}
        mock_tool2.func = lambda x: x + 1
        
        tools = [self.mock_strands_tool, mock_tool2]
        langchain_tools = convert_strands_tools_to_langchain(tools)
        
        self.assertEqual(len(langchain_tools), 2)
        self.assertEqual(langchain_tools[0].name, "test_tool")
        self.assertEqual(langchain_tools[1].name, "test_tool2")
    
    def test_tool_adapter(self):
        """Test ToolAdapter class."""
        adapter = ToolAdapter()
        
        # Test adapting a Strands tool
        langchain_tool = adapter.adapt(self.mock_strands_tool)
        self.assertIsNotNone(langchain_tool)
        self.assertEqual(langchain_tool.name, "test_tool")
        
        # Test cache
        langchain_tool2 = adapter.adapt(self.mock_strands_tool)
        self.assertEqual(langchain_tool, langchain_tool2)
    
    def test_adapt_tool_global(self):
        """Test global adapt_tool function."""
        langchain_tool = adapt_tool(self.mock_strands_tool)
        self.assertIsNotNone(langchain_tool)
        self.assertEqual(langchain_tool.name, "test_tool")
    
    def test_adapt_tools_global(self):
        """Test global adapt_tools function."""
        mock_tool2 = Mock()
        mock_tool2.tool_name = "test_tool2"
        mock_tool2.tool_spec = {"description": "Another test tool"}
        mock_tool2.func = lambda x: x + 1
        
        tools = [self.mock_strands_tool, mock_tool2]
        langchain_tools = adapt_tools(tools)
        
        self.assertEqual(len(langchain_tools), 2)


class TestEventSystem(unittest.TestCase):
    """Test cases for event system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.event_bus = EventBus()
    
    def test_event_creation(self):
        """Test creating events."""
        event = Event(event_type=EventType.AGENT_INITIALIZED)
        self.assertEqual(event.event_type, EventType.AGENT_INITIALIZED)
        self.assertIsNotNone(event.timestamp)
    
    def test_agent_initialized_event(self):
        """Test AgentInitializedEvent."""
        event = AgentInitializedEvent(agent_id="agent-1", agent_name="TestAgent")
        self.assertEqual(event.event_type, EventType.AGENT_INITIALIZED)
        self.assertEqual(event.agent_id, "agent-1")
        self.assertEqual(event.agent_name, "TestAgent")
    
    def test_before_invocation_event(self):
        """Test BeforeInvocationEvent."""
        event = BeforeInvocationEvent(agent_id="agent-1", query="test query")
        self.assertEqual(event.event_type, EventType.BEFORE_INVOCATION)
        self.assertEqual(event.query, "test query")
    
    def test_after_invocation_event(self):
        """Test AfterInvocationEvent."""
        event = AfterInvocationEvent(agent_id="agent-1", result="test result")
        self.assertEqual(event.event_type, EventType.AFTER_INVOCATION)
        self.assertEqual(event.result, "test result")
    
    def test_message_added_event(self):
        """Test MessageAddedEvent."""
        event = MessageAddedEvent(message="Hello", role="user")
        self.assertEqual(event.event_type, EventType.MESSAGE_ADDED)
        self.assertEqual(event.message, "Hello")
        self.assertEqual(event.role, "user")
    
    def test_tool_called_event(self):
        """Test ToolCalledEvent."""
        event = ToolCalledEvent(tool_name="calculator", tool_input={"x": 2})
        self.assertEqual(event.event_type, EventType.TOOL_CALLED)
        self.assertEqual(event.tool_name, "calculator")
    
    def test_tool_result_event(self):
        """Test ToolResultEvent."""
        event = ToolResultEvent(tool_name="calculator", tool_result=4)
        self.assertEqual(event.event_type, EventType.TOOL_RESULT)
        self.assertEqual(event.tool_result, 4)
    
    def test_error_occurred_event(self):
        """Test ErrorOccurredEvent."""
        event = ErrorOccurredEvent(error_message="Test error", error_type="ValueError")
        self.assertEqual(event.event_type, EventType.ERROR_OCCURRED)
        self.assertEqual(event.error_message, "Test error")
    
    def test_event_bus_subscribe(self):
        """Test subscribing to events."""
        callback = Mock()
        self.event_bus.subscribe(EventType.AGENT_INITIALIZED, callback)
        
        event = AgentInitializedEvent(agent_id="agent-1")
        self.event_bus.emit(event)
        
        callback.assert_called_once_with(event)
    
    def test_event_bus_unsubscribe(self):
        """Test unsubscribing from events."""
        callback = Mock()
        self.event_bus.subscribe(EventType.AGENT_INITIALIZED, callback)
        self.event_bus.unsubscribe(EventType.AGENT_INITIALIZED, callback)
        
        event = AgentInitializedEvent(agent_id="agent-1")
        self.event_bus.emit(event)
        
        callback.assert_not_called()
    
    def test_event_bus_history(self):
        """Test event history."""
        event1 = AgentInitializedEvent(agent_id="agent-1")
        event2 = BeforeInvocationEvent(agent_id="agent-1", query="test")
        
        self.event_bus.emit(event1)
        self.event_bus.emit(event2)
        
        history = self.event_bus.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], event1)
        self.assertEqual(history[1], event2)
    
    def test_event_bus_clear_history(self):
        """Test clearing event history."""
        event = AgentInitializedEvent(agent_id="agent-1")
        self.event_bus.emit(event)
        
        self.event_bus.clear_history()
        history = self.event_bus.get_history()
        self.assertEqual(len(history), 0)
    
    def test_global_event_bus(self):
        """Test global event bus."""
        bus = get_event_bus()
        self.assertIsNotNone(bus)
        self.assertIsInstance(bus, EventBus)
    
    def test_emit_event_global(self):
        """Test global emit_event function."""
        callback = Mock()
        subscribe_to_event(EventType.AGENT_INITIALIZED, callback)
        
        event = AgentInitializedEvent(agent_id="agent-1")
        emit_event(event)
        
        callback.assert_called_once()


if __name__ == "__main__":
    unittest.main()


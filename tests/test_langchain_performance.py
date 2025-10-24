"""
Performance benchmarks for LangChain migration.

This module provides performance benchmarks to measure the efficiency of
LangChain agents and swarms compared to baseline expectations.
"""

import pytest
import time
from unittest.mock import Mock, patch
from fivcadvisor.adapters import (
    LangChainAgentAdapter,
    LangGraphSwarmAdapter,
)


class TestLangChainAgentPerformance:
    """Performance tests for LangChain agents"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.mock_tool = Mock()
        self.mock_tool.name = "test_tool"
    
    def test_agent_creation_performance(self, benchmark):
        """Benchmark agent creation time"""
        def create_agent():
            return LangChainAgentAdapter(
                model=self.mock_llm,
                tools=[],
                name="TestAgent",
            )
        
        result = benchmark(create_agent)
        assert isinstance(result, LangChainAgentAdapter)
    
    def test_agent_invocation_performance(self, benchmark):
        """Benchmark agent invocation time"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
        )
        adapter.agent = Mock()
        adapter.agent.invoke = Mock(return_value={"output": "Test response"})
        
        def invoke():
            return adapter.invoke("Test query")
        
        result = benchmark(invoke)
        assert result == "Test response"
    
    def test_agent_with_tools_performance(self, benchmark):
        """Benchmark agent creation with tools"""
        tools = [Mock(name=f"tool_{i}") for i in range(5)]
        
        def create_agent_with_tools():
            return LangChainAgentAdapter(
                model=self.mock_llm,
                tools=tools,
                name="ToolAgent",
            )
        
        result = benchmark(create_agent_with_tools)
        assert isinstance(result, LangChainAgentAdapter)
    
    def test_agent_initialization_overhead(self, benchmark):
        """Benchmark agent initialization overhead"""
        def init_agent():
            adapter = LangChainAgentAdapter(
                model=self.mock_llm,
                tools=[],
                system_prompt="Test prompt",
                name="TestAgent",
            )
            return adapter.agent_id
        
        result = benchmark(init_agent)
        assert result is not None


class TestLangChainSwarmPerformance:
    """Performance tests for LangChain swarms"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
    
    def test_swarm_creation_performance(self, benchmark):
        """Benchmark swarm creation time"""
        agents = [
            LangChainAgentAdapter(model=self.mock_llm, tools=[], name="Agent1"),
            LangChainAgentAdapter(model=self.mock_llm, tools=[], name="Agent2"),
        ]
        
        def create_swarm():
            with patch('fivcadvisor.adapters.multiagent.create_swarm') as mock_create:
                mock_workflow = Mock()
                mock_app = Mock()
                mock_workflow.compile = Mock(return_value=mock_app)
                mock_create.return_value = mock_workflow
                
                return LangGraphSwarmAdapter(agents)
        
        result = benchmark(create_swarm)
        assert isinstance(result, LangGraphSwarmAdapter)
    
    def test_swarm_with_multiple_agents_performance(self, benchmark):
        """Benchmark swarm creation with multiple agents"""
        agents = [
            LangChainAgentAdapter(model=self.mock_llm, tools=[], name=f"Agent{i}")
            for i in range(10)
        ]
        
        def create_large_swarm():
            with patch('fivcadvisor.adapters.multiagent.create_swarm') as mock_create:
                mock_workflow = Mock()
                mock_app = Mock()
                mock_workflow.compile = Mock(return_value=mock_app)
                mock_create.return_value = mock_workflow
                
                return LangGraphSwarmAdapter(agents)
        
        result = benchmark(create_large_swarm)
        assert len(result.agents) == 10


class TestLangChainMemoryUsage:
    """Memory usage tests for LangChain components"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
    
    def test_agent_memory_footprint(self):
        """Test agent memory footprint"""
        import sys
        
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
            name="TestAgent",
        )
        
        # Get size of adapter object
        size = sys.getsizeof(adapter)
        
        # Should be reasonable (less than 10MB)
        assert size < 10 * 1024 * 1024
    
    def test_swarm_memory_footprint(self):
        """Test swarm memory footprint"""
        import sys
        
        agents = [
            LangChainAgentAdapter(model=self.mock_llm, tools=[], name=f"Agent{i}")
            for i in range(5)
        ]
        
        with patch('fivcadvisor.adapters.multiagent.create_swarm') as mock_create:
            mock_workflow = Mock()
            mock_app = Mock()
            mock_workflow.compile = Mock(return_value=mock_app)
            mock_create.return_value = mock_workflow
            
            swarm = LangGraphSwarmAdapter(agents)
            
            # Get size of swarm object
            size = sys.getsizeof(swarm)
            
            # Should be reasonable (less than 50MB)
            assert size < 50 * 1024 * 1024


class TestLangChainThroughput:
    """Throughput tests for LangChain components"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
    
    def test_agent_invocation_throughput(self, benchmark):
        """Benchmark agent invocation throughput"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
        )
        adapter.agent = Mock()
        adapter.agent.invoke = Mock(return_value={"output": "Response"})
        
        def invoke_multiple():
            results = []
            for i in range(10):
                result = adapter.invoke(f"Query {i}")
                results.append(result)
            return results
        
        results = benchmark(invoke_multiple)
        assert len(results) == 10
    
    def test_agent_creation_throughput(self, benchmark):
        """Benchmark agent creation throughput"""
        def create_multiple_agents():
            agents = []
            for i in range(5):
                agent = LangChainAgentAdapter(
                    model=self.mock_llm,
                    tools=[],
                    name=f"Agent{i}",
                )
                agents.append(agent)
            return agents
        
        agents = benchmark(create_multiple_agents)
        assert len(agents) == 5


class TestLangChainLatency:
    """Latency tests for LangChain components"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
    
    def test_agent_invocation_latency(self):
        """Test agent invocation latency"""
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
        )
        adapter.agent = Mock()
        adapter.agent.invoke = Mock(return_value={"output": "Response"})
        
        start = time.time()
        result = adapter.invoke("Test query")
        elapsed = time.time() - start
        
        # Should be very fast (less than 100ms for mock)
        assert elapsed < 0.1
        assert result == "Response"
    
    def test_agent_creation_latency(self):
        """Test agent creation latency"""
        start = time.time()
        adapter = LangChainAgentAdapter(
            model=self.mock_llm,
            tools=[],
            name="TestAgent",
        )
        elapsed = time.time() - start
        
        # Should be fast (less than 50ms)
        assert elapsed < 0.05
        assert adapter.name == "TestAgent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


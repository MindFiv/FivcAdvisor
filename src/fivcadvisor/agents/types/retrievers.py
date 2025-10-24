from abc import ABC, abstractmethod
from typing import Optional, List, Callable, Union, Any
from strands.agent import Agent
from strands.multiagent import MultiAgentBase


class AgentsCreatorBase(ABC):
    """
    Base class for agents creators.

    Supports both Strands Agent and LangChain Agent adapters.
    """

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def description(self):
        raise NotImplementedError()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Union[Agent, MultiAgentBase, Any]:
        """Create and return an agent or multi-agent.

        Returns:
            Agent instance (Strands Agent or LangChain Agent adapter)
        """
        raise NotImplementedError()


class FunctionAgentCreator(AgentsCreatorBase):
    """
    Agent creator that wraps a function.

    Supports both Strands Agent and LangChain Agent adapters.
    """

    def __init__(self, name: str, func: Callable):
        self._name = name
        self._func = func

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._func.__doc__ or ""

    def __call__(self, *args, **kwargs) -> Union[Agent, MultiAgentBase, Any]:
        """Call the wrapped function to create an agent.

        Returns:
            Agent instance (Strands Agent or LangChain Agent adapter)
        """
        return self._func(*args, **kwargs)


class AgentsRetriever(object):
    """
    A retriever for agents.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.agent_creators: dict[str, AgentsCreatorBase] = {}

    def cleanup(self):
        self.agent_creators.clear()

    def add(self, creator: AgentsCreatorBase):
        if creator.name in self.agent_creators:
            raise RuntimeError(f"Agent creator {creator.name} already exists")

        self.agent_creators[creator.name] = creator

    def add_batch(self, creators: List[AgentsCreatorBase]):
        for creator in creators:
            self.add(creator)

    def get(self, name: str) -> Optional[AgentsCreatorBase]:
        return self.agent_creators.get(name)

    def get_batch(self, names: List[str]) -> List[AgentsCreatorBase]:
        return [self.get(name) for name in names]

    def get_all(self) -> List[AgentsCreatorBase]:
        return list(self.agent_creators.values())

    def retrieve(self, query: str) -> List[AgentsCreatorBase]:
        raise NotImplementedError()


def agent_creator(name: str) -> Callable:
    """
    Decorator to convert a function into an AgentsCreatorBase.

    Args:
        name: Name of the agent creator

    Usage:
        @agent_creator("MyAgent")
        def create_my_agent(*args, **kwargs):
            return Agent(...)

        # Then register manually:
        retriever = AgentsRetriever()
        retriever.add(create_my_agent)
    """

    def decorator(func: Callable) -> AgentsCreatorBase:
        # Create the agent creator instance
        creator = FunctionAgentCreator(name or func.__name__, func)

        # Return the creator instance (not the original function)
        return creator

    return decorator

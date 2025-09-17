from typing import Type, Optional, List
from crewai import Flow


class FlowsRetriever(object):
    """
    A retriever for flows.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.flow_types: dict[str, Type[Flow]] = {}

    def cleanup(self):
        self.flow_types.clear()

    def add(self, flow_type: Type[Flow]):
        if flow_type.name in self.flow_types:
            raise ValueError(f"Duplicate flow name: {flow_type.name}")
        self.flow_types[flow_type.name] = flow_type

    def add_batch(self, flow_types: List[Type[Flow]]):
        for flow_type in flow_types:
            self.add(flow_type)

    def get(self, name: str) -> Optional[Type[Flow]]:
        return self.flow_types.get(name)

    def get_batch(self, names: List[str]) -> List[Type[Flow]]:
        return [self.get(name) for name in names]

    def retrieve(self, query: str) -> List[Type[Flow]]:
        raise NotImplementedError()

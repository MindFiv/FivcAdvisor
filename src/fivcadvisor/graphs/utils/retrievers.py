from typing import Optional, List
from .base import Graph


class GraphsRetriever(object):
    """
    A retriever for graphs.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.graph_builders: dict[str, Graph] = {}

    def cleanup(self):
        self.graph_builders.clear()

    def add(self, graph: Graph):
        if graph.name in self.graph_builders:
            # Allow re-registration of the same graph type (idempotent operation)
            # This prevents errors when multiple entry points try to register default graphs
            return
        self.graph_builders[graph.name] = graph

    def add_batch(self, graphs: List[Graph]):
        for graph_type in graphs:
            self.add(graph_type)

    def get(self, name: str) -> Optional[Graph]:
        return self.graph_builders.get(name)

    def get_batch(self, names: List[str]) -> List[Graph]:
        return [self.get(name) for name in names]

    def retrieve(self, query: str) -> List[Graph]:
        raise NotImplementedError()

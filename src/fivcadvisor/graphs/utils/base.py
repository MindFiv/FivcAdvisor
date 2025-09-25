__all__ = [
    "Graph",
]

from typing import Any, Optional

from pydantic import BaseModel
from langgraph.graph import StateGraph

from fivcadvisor import utils


class GraphState(BaseModel):
    """Base state for all graphs."""

    tools_retriever: Optional[Any]
    run_id: Optional[str]
    verbose: bool = True
    user_query: str
    final_result: Optional[str] = ""
    error: Optional[str] = None


class GraphRun(object):
    """Result of running a graph."""

    def __init__(self, compiled_graph, **kwargs):
        self.compiled_graph = compiled_graph
        self.kwargs = kwargs

    def plot(self, name):
        self.compiled_graph.get_graph().draw_png(f"{name}.png")

    def kickoff(self, inputs=None, **kwargs):
        inputs = inputs or {}
        inputs = utils.create_default_kwargs(inputs, self.kwargs)
        return self.compiled_graph.invoke(inputs, **kwargs)

    async def kickoff_async(self, inputs=None, **kwargs):
        inputs = inputs or {}
        inputs = utils.create_default_kwargs(inputs, self.kwargs)
        return await self.compiled_graph.ainvoke(inputs, **kwargs)


class Graph(object):
    """
    Base class for all graphs.
    """

    def __init__(
        self,
        name: str,
        description: str,
        builder: StateGraph,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.builder = builder

    def __call__(self, *args, **kwargs):
        return GraphRun(
            self.builder.compile(),
            **kwargs,
        )

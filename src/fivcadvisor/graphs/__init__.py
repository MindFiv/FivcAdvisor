from fivcadvisor.utils import create_lazy_value

from .complex import create_complex_graph
from .general import create_general_graph
from .simple import create_simple_graph


def create_retriever(*args, **kwargs):
    """Create a graphs retriever tool."""
    from .utils.retrievers import GraphsRetriever

    return GraphsRetriever(*args, **kwargs)


# def create_evaluating_graph(*args, **kwargs):
#     raise NotImplementedError("Graph not implemented")
#
#
# def create_engineering_graph(*args, **kwargs):
#     raise NotImplementedError("Graph not implemented")


def register_default_graphs(*args, graphs_retriever=None, **kwargs):
    """Create a default graph instance."""

    assert graphs_retriever is not None

    graph_types = [
        create_general_graph(),
        create_simple_graph(),
        create_complex_graph(),
    ]
    graphs_retriever.add_batch(graph_types)
    return graph_types


def _load():
    retriever = create_retriever()
    register_default_graphs(graphs_retriever=retriever)
    return retriever


default_retriever = create_lazy_value(_load)

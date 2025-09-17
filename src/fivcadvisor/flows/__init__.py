from fivcadvisor import utils


def create_retriever(*args, **kwargs):
    """Create a tools retriever tool."""
    from .utils.retrievers import FlowsRetriever

    return FlowsRetriever(*args, **kwargs)


def create_general_flow(*args, **kwargs):
    """Create a GeneralFlow instance.

    Args:
        *args: Additional arguments passed to GeneralFlow
        **kwargs: Additional keyword arguments passed to GeneralFlow

    Returns:
        GeneralFlow: A configured GeneralFlow instance
    """
    from .general import GeneralFlow

    return GeneralFlow(*args, **kwargs)


def create_simple_flow(*args, **kwargs):
    """Create a DefaultSimpleFlow instance.

    Args:
        *args: Additional arguments passed to DefaultSimpleFlow
        **kwargs: Additional keyword arguments passed to DefaultSimpleFlow

    Returns:
        DefaultSimpleFlow: A configured DefaultSimpleFlow instance
    """
    from .simple import SimpleFlow

    return SimpleFlow(*args, **kwargs)


def create_complex_flow(*args, **kwargs):
    """Create a ComplexFlow instance.

    Args:
        *args: Additional arguments passed to ComplexFlow
        **kwargs: Additional keyword arguments passed to ComplexFlow

    Returns:
        ComplexFlow: A configured ComplexFlow instance
    """
    from .complex import ComplexFlow

    return ComplexFlow(*args, **kwargs)


def create_evaluating_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")


def create_engineering_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")


def create_default_flow(*args, flows_retriever=None, **kwargs):
    """Create a default flow instance."""
    from .utils.retrievers import FlowsRetriever

    assert isinstance(flows_retriever, FlowsRetriever)

    from .general import GeneralFlow
    from .simple import SimpleFlow
    from .complex import ComplexFlow

    flow_types = [
        GeneralFlow,
        SimpleFlow,
        ComplexFlow,
    ]
    flows_retriever.add_batch(flow_types)
    return flow_types


def _load():
    retriever = create_retriever()
    create_default_flow(flows_retriever=retriever)
    return retriever


default_retriever = utils.create_lazy_value(_load)

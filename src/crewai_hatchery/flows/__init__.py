from .default import DefaultFlow


def create_default_flow(user_query: str = None, *args, **kwargs):
    """Create a DefaultFlow instance.

    Args:
        user_query (str, optional): The user query to process. If not provided,
                                   the flow will prompt for input interactively.
        *args: Additional arguments passed to DefaultFlow
        **kwargs: Additional keyword arguments passed to DefaultFlow

    Returns:
        DefaultFlow: A configured DefaultFlow instance
    """
    return DefaultFlow(user_query=user_query, **kwargs)


def create_evaluating_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")


def create_engineering_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")

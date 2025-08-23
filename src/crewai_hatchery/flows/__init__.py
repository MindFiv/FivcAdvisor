def create_default_flow(*args, **kwargs):
    """Create a DefaultFlow instance.

    Args:
        *args: Additional arguments passed to DefaultFlow
        **kwargs: Additional keyword arguments passed to DefaultFlow

    Returns:
        DefaultFlow: A configured DefaultFlow instance
    """
    from .default import DefaultFlow

    return DefaultFlow(*args, **kwargs)


def create_evaluating_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")


def create_engineering_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")

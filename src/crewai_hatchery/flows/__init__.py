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


def create_default_simple_flow(*args, **kwargs):
    """Create a DefaultSimpleFlow instance.

    Args:
        *args: Additional arguments passed to DefaultSimpleFlow
        **kwargs: Additional keyword arguments passed to DefaultSimpleFlow

    Returns:
        DefaultSimpleFlow: A configured DefaultSimpleFlow instance
    """
    from .default_simple import DefaultSimpleFlow

    return DefaultSimpleFlow(*args, **kwargs)


def create_default_complex_flow(*args, **kwargs):
    """Create a DefaultComplexFlow instance.

    Args:
        *args: Additional arguments passed to DefaultComplexFlow
        **kwargs: Additional keyword arguments passed to DefaultComplexFlow

    Returns:
        DefaultComplexFlow: A configured DefaultComplexFlow instance
    """
    from .default_complex import DefaultComplexFlow

    return DefaultComplexFlow(*args, **kwargs)


def create_evaluating_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")


def create_engineering_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")

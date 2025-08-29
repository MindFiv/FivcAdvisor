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
    """Create a DefaultComplexFlow instance.

    Args:
        *args: Additional arguments passed to DefaultComplexFlow
        **kwargs: Additional keyword arguments passed to DefaultComplexFlow

    Returns:
        DefaultComplexFlow: A configured DefaultComplexFlow instance
    """
    from .complex import ComplexFlow

    return ComplexFlow(*args, **kwargs)


def create_evaluating_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")


def create_engineering_flow(*args, **kwargs):
    raise NotImplementedError("Flow not implemented")

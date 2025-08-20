__all__ = [
    "create_default_kwargs",
    "create_lazy_value",
    "create_output_dir",
]

from typing import Optional, Callable


def create_default_kwargs(kwargs: dict, defaults: dict):
    """
    Create default kwargs from a defaults dict.
    """
    for k, v in defaults.items():
        if kwargs.get(k) is None:
            kwargs[k] = v
    return kwargs


def create_lazy_value(getter: Callable):
    """Create a LazyValue proxy from a factory callable."""
    from .lazy import LazyValue

    return LazyValue(getter)


def create_output_dir(base: Optional[str] = None):
    """
    Create an output directory for CrewAI Hatchery.
    """
    from .directories import OutputDir

    return OutputDir(base)

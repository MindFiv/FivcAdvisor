__all__ = [
    "create_default_logger",
    "create_agent_logger",
    "agent_logger",
    "default_logger",
]

from json import dumps

from fivcadvisor import utils, settings


def create_default_logger(**kwargs):
    """Create a default logger.

    Args:
        **kwargs: Configuration options including:
            - name: Logger name
            - level: Logging level (e.g., 'INFO', 'DEBUG')
            - file: File path for file logging
            - console: Boolean to control console output (default: False when file is specified)
            - format: Log message format string

    Returns:
        Logger: Configured logger instance

    Note:
        When 'file' is specified, console output is disabled by default to prevent
        duplicate output to stderr/stdout. Set console=True to enable both file and console output.
        Logger propagation is disabled when using file-only logging to prevent parent
        logger handlers from outputting to console.
    """
    from logging import (
        getLogger,
        Formatter,
        StreamHandler,
        handlers,
    )

    kwargs = utils.create_default_kwargs(kwargs, settings.default_logger_config)

    logger_name = kwargs.pop("name", None)
    logger = getLogger(logger_name)

    logger_level = kwargs.pop("level", None)
    if isinstance(logger_level, str):
        logger.setLevel(logger_level)

    # Control console output explicitly
    console_output = kwargs.pop("console", None)
    logger_file = kwargs.pop("file", None)

    # Clear any existing handlers to avoid duplication
    logger.handlers.clear()
    logger_handlers = []

    # Add file handler if specified
    if isinstance(logger_file, str):
        logger_handlers.append(
            handlers.RotatingFileHandler(
                logger_file,
                mode="a+",
                maxBytes=1048576,  # 1MB
                backupCount=7,
            )
        )
        # When file is specified, disable console output by default
        if console_output is None:
            console_output = False

    # Add console handler if explicitly requested or if no file handler
    if console_output is True or (console_output is None and not logger_file):
        logger_handlers.append(StreamHandler())

    # Prevent propagation to parent loggers when file logging is used
    # This prevents output to stderr/stdout from parent logger handlers
    if logger_file and not console_output:
        logger.propagate = False

    logger_fmt = kwargs.pop("format", None)
    logger_fmt = Formatter(logger_fmt) if isinstance(logger_fmt, str) else None

    for handler in logger_handlers:
        if logger_fmt:
            handler.setFormatter(logger_fmt)
        logger.addHandler(handler)

    return logger


def create_agent_logger(**kwargs):
    """Create a logger for agents."""
    kwargs = utils.create_default_kwargs(kwargs, settings.agent_logger_config)
    kwargs["name"] = "agent"
    logger = create_default_logger(**kwargs)

    # register to crewai event bus
    from crewai import LLM

    from crewai.tools.tool_usage import ToolUsage
    from crewai.utilities.events import (
        base_events,
        # agent_events,
        # flow_events,
        crewai_event_bus,
    )

    @crewai_event_bus.on(base_events.BaseEvent)
    def _on_event(source, event):
        if isinstance(source, LLM):
            return  # skip llm events

        if isinstance(source, ToolUsage):
            source = source.agent

        event_info = event.to_json()
        event_session = getattr(source, "session_id", "")

        # if isinstance(event, agent_events.AgentLogsExecutionEvent):
        #     event.formatted_answer

        logger.info(
            dumps(
                {
                    "session_id": event_session,
                    "event": event_info,
                }
            )
        )

    return logger


default_logger = utils.create_lazy_value(create_default_logger)
agent_logger = utils.create_lazy_value(create_agent_logger)

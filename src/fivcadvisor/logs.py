__all__ = [
    "create_default_logger",
    "create_agent_logger",
    "agent_logger",
    "default_logger",
]

from json import dumps

from fivcadvisor import utils, settings


def create_default_logger(**kwargs):
    """Create a default logger."""
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

    logger_handlers = []
    logger_file = kwargs.pop("file", None)
    if isinstance(logger_file, str):
        logger_handlers.append(
            handlers.RotatingFileHandler(
                logger_file,
                mode="a+",
                maxBytes=1048576,  # 1MB
                backupCount=7,
            )
        )
    else:
        logger_handlers.append(StreamHandler())

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

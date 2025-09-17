__all__ = ["default_manager"]

from asyncio import Queue
from uuid import uuid4

from fivcadvisor import utils


class SessionManager(object):
    """Manager for handling multiple sessions."""

    def __init__(self):
        self.sessions = {}

    def create_session(self):
        """Create a new session."""
        return Session(self)


class Session(object):
    """Session for managing flow execution."""

    def __init__(self, manager):
        self.id = str(uuid4())
        self.manager = manager
        self.events = Queue()

    def __enter__(self):
        self.manager.sessions[self.id] = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.manager.sessions.pop(self.id)
        self.events.shutdown()

    async def get_event(self):
        return await self.events.get()

    async def put_event(self, event):
        await self.events.put(event)


def _load():
    m = SessionManager()

    from crewai import LLM
    from crewai.tools.tool_usage import ToolUsage
    from crewai.utilities.events import (
        base_events,
        # agent_events,
        crewai_event_bus,
    )

    @crewai_event_bus.on(base_events.BaseEvent)
    def _on_event(source, event):
        if isinstance(source, LLM):
            return  # skip llm events

        if isinstance(source, ToolUsage):
            source = source.agent

        session_id = getattr(source, "session_id", "")
        session = m.sessions.get(session_id)
        if not session:
            return

        session.put_event(event)

    return m


default_manager = utils.create_lazy_value(_load)

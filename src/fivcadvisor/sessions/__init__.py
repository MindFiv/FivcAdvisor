import json
from fivcadvisor import utils


def create_file_session_manager(output_dir=None, **kwargs):
    """
    Create a file session manager.
    Args:
        output_dir:
        **kwargs:

    Returns:

    """

    output_dir = output_dir or utils.create_output_dir().subdir("sessions")

    from .files import FileSessionManager

    return FileSessionManager(str(output_dir))


def register_default_events(session_manager=None, **kwargs):
    """Create a listener that logs events."""
    assert session_manager is not None

    from crewai.utilities.events import (
        crewai_event_bus,
        base_events,
        # llm_events,
    )

    @crewai_event_bus.on(base_events.BaseEvent)
    def _on_event(source, event):
        session_id = getattr(source, "session_id", "")
        if not session_id:
            source = getattr(source, "agent", None)
            session_id = getattr(source, "session_id", None)

        session = session_manager.get_session(session_id)
        if not session:
            print(f"Session not found for {source}")
            return

        info = event.to_json()
        info["session_id"] = session_id
        session.put(json.dumps(info))


default_manager = utils.create_lazy_value(create_file_session_manager)

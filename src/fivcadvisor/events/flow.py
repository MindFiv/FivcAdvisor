from typing import Callable, Any, Dict, Optional

from pydantic import BaseModel


class FlowEvent(BaseModel):
    session_id: str


class FlowEventAgent(FlowEvent):
    agent_id: str
    agent_role: str


class FlowEventAgentStarted(FlowEventAgent):
    query: str


class FlowEventAgentCompleted(FlowEventAgent):
    output: str


class FlowEventTask(FlowEvent):
    task_id: str
    task_name: str


class FlowEventTaskStarted(FlowEventTask):
    """Task started event."""


class FlowEventTaskCompleted(FlowEventTask):
    output: str


class FlowEventCrew(FlowEvent):
    crew_id: str
    crew_name: str


class FlowEventCrewStarted(FlowEventCrew):
    """Crew started event."""

    inputs: Optional[Dict[str, Any]] = None


class FlowEventCrewCompleted(FlowEventCrew):
    """Crew completed event."""

    output: Optional[Dict[str, Any]] = None


def register_flow_events(callback: Callable, **kwargs):
    """Create a listener that logs events."""

    from crewai.utilities.events import (
        crewai_event_bus,
        agent_events,
        task_events,
        crew_events,
    )

    @crewai_event_bus.on(agent_events.AgentExecutionStartedEvent)
    def _on_agent_started(source, event):
        callback(
            FlowEventAgentStarted(
                session_id=source.session_id,
                agent_id=str(source.id),
                agent_role=source.role,
                query=event.task_prompt,
            )
        )

    @crewai_event_bus.on(agent_events.AgentExecutionCompletedEvent)
    def _on_agent_completed(source, event):
        callback(
            FlowEventAgentCompleted(
                session_id=source.session_id,
                agent_id=str(source.id),
                agent_role=source.role,
                output=event.output,
            )
        )

    @crewai_event_bus.on(task_events.TaskStartedEvent)
    def _on_task_started(source, event):
        callback(
            FlowEventTaskStarted(
                session_id=source.session_id,
                task_id=str(source.id),
                task_name=source.name,
            )
        )

    @crewai_event_bus.on(task_events.TaskCompletedEvent)
    def _on_task_completed(source, event):
        callback(
            FlowEventTaskCompleted(
                session_id=source.session_id,
                task_id=str(source.id),
                task_name=source.name,
                output=event.output.raw,
            )
        )

    @crewai_event_bus.on(crew_events.CrewKickoffStartedEvent)
    def _on_crew_started(source, event):
        callback(
            FlowEventCrewStarted(
                session_id=source.session_id,
                crew_id=str(source.id),
                crew_name=source.name,
                inputs=event.inputs,
            )
        )

    @crewai_event_bus.on(crew_events.CrewKickoffCompletedEvent)
    def _on_crew_completed(source, event):
        callback(
            FlowEventCrewCompleted(
                session_id=source.session_id,
                crew_id=str(source.id),
                crew_name=source.name,
                output=event.output.to_dict(),
            )
        )

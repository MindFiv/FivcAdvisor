from typing import Callable, Optional, Any

from pydantic import BaseModel


class UIEvent(BaseModel):
    """Base UI event."""

    session_id: str
    task_id: str
    task_name: str


class UIEventTaskStarted(UIEvent):
    """Task started event."""


class UIEventTaskCompleted(UIEvent):
    """Task completed event."""

    output: str


class UIEventTaskFailed(UIEvent):
    """Task failed event."""

    error: str


class UIEventTaskProgress(UIEvent):
    """Task progress event."""

    agent_id: Optional[str] = None
    agent_role: Optional[str] = None


class UIEventTaskProgressStarted(UIEventTaskProgress):
    """Task progress started event."""

    messages: Optional[list[dict[str, Any]]] = None


class UIEventTaskProgressCompleted(UIEventTaskProgress):
    """Task progress completed event."""

    messages: Optional[list[dict[str, Any]]] = None


class UIEventTaskProgressStream(UIEventTaskProgress):
    """Task progress stream event."""

    chunk: str


def register_ui_events(callback: Callable, **kwargs):
    """Create a listener that logs events."""
    from crewai.utilities.events import (
        crewai_event_bus,
        llm_events,
        task_events,
        tool_usage_events,
    )

    @crewai_event_bus.on(llm_events.LLMCallStartedEvent)
    def _on_llm_started(source, event):
        callback(
            UIEventTaskProgressStarted(
                session_id=source.session_id,
                task_id=event.task_id,
                task_name=event.task_name,
                agent_id=event.agent_id,
                agent_role=event.agent_role,
                messages=event.messages,
            )
        )

    @crewai_event_bus.on(llm_events.LLMCallCompletedEvent)
    def _on_llm_completed(source, event):
        callback(
            UIEventTaskProgressCompleted(
                session_id=source.session_id,
                task_id=event.task_id,
                task_name=event.task_name,
                agent_id=event.agent_id,
                agent_role=event.agent_role,
                messages=event.messages,
            )
        )

    # @crewai_event_bus.on(llm_events.LLMCallFailedEvent)
    # def _on_llm_failed(source, event):
    #     callback(EventTaskProgress(
    #         session_id=source.session_id,
    #         task_id=event.task_id,
    #         task_name=event.task_name,
    #         agent_id=event.agent_id,
    #         agent_role=event.agent_role,
    #         error=event.error,
    #     ))

    @crewai_event_bus.on(llm_events.LLMStreamChunkEvent)
    def _on_llm_stream(source, event):
        callback(
            UIEventTaskProgressStream(
                session_id=source.session_id,
                task_id=event.task_id,
                task_name=event.task_name,
                agent_id=event.agent_id,
                agent_role=event.agent_role,
                chunk=event.chunk,
            )
        )

    @crewai_event_bus.on(task_events.TaskStartedEvent)
    def _on_task_started(source, event):
        callback(
            UIEventTaskStarted(
                session_id=source.session_id,
                task_id=str(source.id),
                task_name=source.name,
            )
        )

    @crewai_event_bus.on(task_events.TaskCompletedEvent)
    def _on_task_completed(source, event):
        callback(
            UIEventTaskCompleted(
                session_id=source.session_id,
                task_id=str(source.id),
                task_name=source.name,
                output=event.output.raw,
            )
        )

    @crewai_event_bus.on(task_events.TaskFailedEvent)
    def _on_task_failed(source, event):
        callback(
            UIEventTaskFailed(
                session_id=source.session_id,
                task_id=str(source.id),
                task_name=source.name,
                error=event.error,
            )
        )

    @crewai_event_bus.on(tool_usage_events.ToolUsageEvent)
    def _on_tool_usage(source, event):
        # TODO: Add tool usage event
        pass

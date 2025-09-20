"""
Server routes for FivcAdvisor server.

This module defines FastAPI routes for flow execution and management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from fivcadvisor.logs import default_logger
from fivcadvisor.sessions import default_manager as session_manager
from fivcadvisor.flows import default_retriever as flows_retriever
from fivcadvisor.tools import default_retriever as tools_retriever

from .models import (
    FlowExecuteRequest,
    FlowExecuteResponse,
)

# Create API router
router = APIRouter()


@router.post(
    "/flows/{flow_type}/execute",
    response_model=FlowExecuteResponse,
)
async def execute_flow(
    flow_type: str,
    request: FlowExecuteRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Execute a flow with the given parameters."""

    if not request.user_query:
        raise HTTPException(
            status_code=400,
            detail="user_query cannot be empty",
        )

    flow_class = flows_retriever.get(flow_type)
    if not flow_class:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown flow type: {flow_type}",
        )

    flow_session = session_manager.create_session()
    if not flow_session:
        raise HTTPException(
            status_code=500,
            detail="Failed to create session",
        )

    def _execute():
        """Execute the flow in a background task."""
        try:
            with flow_session as s:
                flow = flow_class(
                    tools_retriever=tools_retriever(),
                    session_id=s.id,
                )
                flow.kickoff(inputs={"user_query": request.user_query})
        except Exception as e:
            default_logger.error(f"Error executing flow: {e}")

    background_tasks.add_task(_execute)

    return FlowExecuteResponse(
        thread_id=request.thread_id,
        run_id=flow_session.id,
    )


@router.post("/runs/{run_id}/inspect")
async def inspect_run(run_id: str):
    """Inspect a flow session."""

    flow_session = session_manager.get_session(run_id)
    if flow_session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    def _inspect():
        try:
            while True:
                flow_event = flow_session.get(timeout=3.0)
                if not flow_event:
                    continue

                yield f"{flow_event}\n\n"

        except Exception as e:
            default_logger.error(f"Error inspecting session: {e}")

    return StreamingResponse(
        _inspect(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )

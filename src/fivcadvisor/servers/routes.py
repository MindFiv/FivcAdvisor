"""
Server routes for FivcAdvisor server.

This module defines FastAPI routes for flow execution and management.
"""

import time
import traceback
import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from fivcadvisor.flows import default_retriever as flows_retriever
from fivcadvisor.tools import default_retriever as tools_retriever
from .models import (
    FlowExecuteRequest,
    FlowExecuteResponse,
)
from .sessions import default_manager as session_manager

# Create API router
router = APIRouter()


@router.post("/flows/{flow_type}/execute")
async def execute_flow(
    flow_type: str,
    request: FlowExecuteRequest,
    # background_tasks: BackgroundTasks,
):
    """Execute a flow with the given parameters."""

    # Validate flow type first
    flow_class = flows_retriever.get(flow_type)
    if not flow_class:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown flow type: {flow_type}",
        )

    if not request.user_query:
        raise HTTPException(
            status_code=400,
            detail="user_query cannot be empty",
        )

    async def generate_flow_response():
        """Generator function for streaming response."""
        start_time = time.time()

        try:
            with session_manager.create_session() as session:
                from crewai.utilities.events import FlowFinishedEvent

                flow = flow_class(
                    tools_retriever=tools_retriever(),
                    session_id=session.id,
                    # verbose=request.verbose,
                )

                # Run the flow in a background task so we can concurrently listen to events
                flow_task = asyncio.create_task(
                    flow.kickoff_async(inputs={"user_query": request.user_query})
                )

                try:
                    # Wait for either the flow to complete or the finish event
                    while not flow_task.done():
                        try:
                            # Use timeout to avoid indefinite blocking on event queue
                            event = await asyncio.wait_for(
                                session.events.get(), timeout=1.0
                            )
                        except asyncio.TimeoutError:
                            # Periodically check if the flow finished without emitting events
                            continue

                        if isinstance(event, FlowFinishedEvent):
                            print("FlowFinishedEvent")
                            break
                        else:
                            # Stream out event payloads as they arrive
                            event_data = {"event": event.to_json()}
                            yield f"data: {json.dumps(event_data)}\n\n"

                    # Flow has completed (or finish event received); await result
                    flow_result = await flow_task
                    flow_task.result()

                except Exception as e:
                    # Ensure the flow task is cancelled on error
                    if not flow_task.done():
                        flow_task.cancel()
                        try:
                            await flow_task
                        except asyncio.CancelledError:
                            pass
                    raise e

            # Send final response
            final_response = FlowExecuteResponse(
                result=flow_result,
                error=None,
                error_detail={
                    "flow_type": flow_type,
                    "user_query": request.user_query,
                },
                execution_time=time.time() - start_time,
            )
            yield f"data: {json.dumps(final_response.model_dump())}\n\n"

        except Exception as e:
            # Send error response
            error_response = FlowExecuteResponse(
                result=None,
                error=str(e),
                error_detail={
                    "flow_type": flow_type,
                    "user_query": request.user_query,
                    "callstack": traceback.format_exc(),
                },
                execution_time=time.time() - start_time,
            )
            yield f"data: {json.dumps(error_response.model_dump())}\n\n"

    return StreamingResponse(
        generate_flow_response(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )

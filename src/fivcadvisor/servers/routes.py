"""
Server routes for FivcAdvisor server.

This module defines FastAPI routes for flow execution and management.
"""

import time
import traceback

from fastapi import APIRouter, HTTPException

from fivcadvisor.flows import default_retriever as flows_retriever
from fivcadvisor.tools import default_retriever as tools_retriever
from .models import (
    FlowExecuteRequest,
    FlowExecuteResponse,
)
from .sessions import default_manager as session_manager

# Create API router
router = APIRouter()


@router.post("/flows/{flow_type}/execute", response_model=FlowExecuteResponse)
async def execute_flow(
    flow_type: str,
    request: FlowExecuteRequest,
    # background_tasks: BackgroundTasks,
):
    """Execute a flow with the given parameters."""
    start_time = time.time()

    flow_type = flows_retriever.get(flow_type)
    if not flow_type:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown flow type: {flow_type}. ",
        )

    if not request.user_query:
        raise HTTPException(
            status_code=400,
            detail="user_query cannot be empty",
        )

    try:
        with session_manager.create_session() as session:
            from crewai.utilities.events import FlowFinishedEvent

            flow = flow_type(
                tools_retriever=tools_retriever(),
                session_id=session.id,
                # verbose=request.verbose,
            )
            flow_coroutine = flow.kickoff_async(
                inputs={"user_query": request.user_query}
            )

            while True:
                event = await session.get_event()
                if isinstance(event, FlowFinishedEvent):
                    print(f"Flow finished {event}")
                    break

            flow_result = await flow_coroutine

        return FlowExecuteResponse(
            result=flow_result,
            error=None,
            error_detail={
                "flow_type": flow_type,
                "user_query": request.user_query,
            },
            execution_time=time.time() - start_time,
        )

    except Exception as e:
        return FlowExecuteResponse(
            result=None,
            error=str(e),
            error_detail={
                "flow_type": flow_type,
                "user_query": request.user_query,
                "callstack": traceback.format_exc(),
            },
            execution_time=time.time() - start_time,
        )

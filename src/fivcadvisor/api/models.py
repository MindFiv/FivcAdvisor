"""
Server schemas for FivcAdvisor server.

This module defines Pydantic schemas for server requests and responses.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


# flow schemas ----------------------------------------------------------
class FlowExecuteRequest(BaseModel):
    """Request schema for flow execution."""

    thread_id: Optional[str] = Field(None, description="Thread ID")
    user_query: str = Field(..., description="The user query to process")
    # verbose: bool = Field(False, description="Enable verbose output")
    config: Optional[Dict[str, Any]] = Field(
        None, description="Optional configuration parameters"
    )


class FlowExecuteResponse(BaseModel):
    """Response schema for flow execution."""

    thread_id: Optional[str] = Field(None, description="Thread ID")
    run_id: str = Field(..., description="Run ID")

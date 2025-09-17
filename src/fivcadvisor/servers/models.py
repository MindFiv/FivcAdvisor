"""
Server schemas for FivcAdvisor server.

This module defines Pydantic schemas for server requests and responses.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


# flow schemas ----------------------------------------------------------
class FlowExecuteRequest(BaseModel):
    """Request schema for flow execution."""

    user_query: str = Field(..., description="The user query to process")
    # verbose: bool = Field(False, description="Enable verbose output")
    config: Optional[Dict[str, Any]] = Field(
        None, description="Optional configuration parameters"
    )


class FlowExecuteResponse(BaseModel):
    """Response schema for flow execution."""

    result: Optional[Any] = Field(None, description="Flow execution result")
    error: Optional[str] = Field(None, description="Error message if status is error")
    error_detail: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    execution_time: Optional[float] = Field(
        None, description="Execution time in seconds"
    )

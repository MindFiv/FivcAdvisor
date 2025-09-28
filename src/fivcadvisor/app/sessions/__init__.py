from enum import Enum
from typing import List, Optional
from uuid import uuid4
import threading
import time

import streamlit as st
from pydantic import BaseModel


class SessionExecutionStatus(Enum):
    """Session execution status."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class SessionExecutionTask(BaseModel):
    """Session execution task model."""

    agent_id: str
    agent_role: str
    task_id: str
    task_name: str
    thoughts: List[str] = []
    streaming: bool = False  # if it is streaming


class SessionMessage(BaseModel):
    """Session message model."""

    role: str
    content: str
    tasks: List[SessionExecutionTask] = []
    # cards: Optional[str] = None


class SessionData(BaseModel):
    """Session status model."""

    mode: str = "general"  # general, simple, complex
    user_query: str = ""  # current user query that is being processed
    messages: List[SessionMessage] = []
    is_processing: bool = False  # explicit processing state for immediate UI feedback

    # Async execution fields
    execution_status: SessionExecutionStatus = SessionExecutionStatus.IDLE
    progress_message: str = ""
    execution_error: Optional[str] = None
    execution_result: Optional[str] = None


class Session(object):
    """
    A session manager for FivcAdvisor applications.

    This class provides a central point for managing session state
    and ensuring consistent access across different components.
    """

    def __init__(
        self,
        agents_retriever=None,
        tools_retriever=None,
    ):
        """Initialize the session manager."""
        if "session_data" not in st.session_state:
            st.session_state.session_data = SessionData()

        assert agents_retriever is not None
        self.agents_retriever = agents_retriever
        assert tools_retriever is not None
        self.tools_retriever = tools_retriever

        # Thread management
        self._execution_thread: Optional[threading.Thread] = None
        self._execution_lock = threading.Lock()
        self._cancel_flag = threading.Event()

    def get_messages(self):
        """Get the chat messages."""
        return st.session_state.session_data.messages

    def add_message(self, message: SessionMessage):
        """Add a message to the chat."""
        st.session_state.session_data.messages.append(message)

    def clear_messages(self):
        """Clear the chat messages."""
        st.session_state.session_data.messages.clear()

    @property
    def is_processing(self):
        """Check if there is a query being processed."""
        return (
            st.session_state.session_data.is_processing
            or bool(st.session_state.session_data.user_query)
            or st.session_state.session_data.execution_status
            == SessionExecutionStatus.RUNNING
        )

    @property
    def execution_status(self):
        """Get current execution status."""
        return st.session_state.session_data.execution_status

    @property
    def progress_message(self):
        """Get current progress message."""
        return st.session_state.session_data.progress_message

    def ask(self, query: str):
        """Ask a question."""
        if self.is_processing:
            raise ValueError("Previous query not answered")
        # Immediately set processing state for instant UI feedback
        st.session_state.session_data.is_processing = True
        st.session_state.session_data.user_query = query
        st.session_state.session_data.execution_status = SessionExecutionStatus.IDLE
        st.session_state.session_data.progress_message = ""
        st.session_state.session_data.execution_error = None
        st.session_state.session_data.execution_result = None

    def run(self):
        """Create a graph run (non-blocking)."""
        user_query = st.session_state.session_data.user_query
        if not user_query:
            # Check if we have a completed execution
            self._check_execution_status()
            return

        # Clear the user query and start async execution
        st.session_state.session_data.user_query = ""
        st.session_state.session_data.is_processing = False
        self.add_message(SessionMessage(role="user", content=user_query))

        # Start async execution
        self._start_async_execution(user_query)

    def _start_async_execution(self, user_query: str):
        """Start async execution of the agent."""
        with self._execution_lock:
            # Cancel any existing execution
            if self._execution_thread and self._execution_thread.is_alive():
                self._cancel_flag.set()
                self._execution_thread.join(timeout=1.0)

            # Reset cancel flag and start new execution
            self._cancel_flag.clear()
            st.session_state.session_data.execution_status = (
                SessionExecutionStatus.RUNNING
            )
            st.session_state.session_data.progress_message = (
                "Starting agent execution..."
            )

            # Start execution thread
            self._execution_thread = threading.Thread(
                target=self._execute_agent_async, args=(user_query,), daemon=True
            )
            self._execution_thread.start()

        # Schedule a rerun to update UI
        st.rerun()

    def _execute_agent_async(self, user_query: str):
        """Execute agent in background thread."""
        try:
            # Update progress
            st.session_state.session_data.progress_message = "Initializing graph..."

            graph = self.agents_retriever.get(st.session_state.session_data.mode)
            if not graph:
                raise RuntimeError(
                    f"Graph not found for mode: {st.session_state.session_data.mode}"
                )

            # Check for cancellation
            if self._cancel_flag.is_set():
                st.session_state.session_data.execution_status = (
                    SessionExecutionStatus.CANCELLED
                )
                return

            st.session_state.session_data.progress_message = "Creating graph run..."
            graph_run = graph(
                tools_retriever=self.tools_retriever,
                verbose=False,
                run_id=str(uuid4()),
            )

            # Check for cancellation
            if self._cancel_flag.is_set():
                st.session_state.session_data.execution_status = (
                    SessionExecutionStatus.CANCELLED
                )
                return

            st.session_state.session_data.progress_message = "Executing agent..."
            result = graph_run.kickoff(inputs={"user_query": user_query})

            # Check for cancellation
            if self._cancel_flag.is_set():
                st.session_state.session_data.execution_status = (
                    SessionExecutionStatus.CANCELLED
                )
                return

            # Process result
            result_text = result.get("final_result") or ""
            st.session_state.session_data.execution_result = result_text
            st.session_state.session_data.execution_status = (
                SessionExecutionStatus.COMPLETED
            )
            st.session_state.session_data.progress_message = (
                "Execution completed successfully"
            )

        except Exception as e:
            st.session_state.session_data.execution_error = str(e)
            st.session_state.session_data.execution_status = (
                SessionExecutionStatus.ERROR
            )
            st.session_state.session_data.progress_message = (
                f"Execution failed: {str(e)}"
            )

    def _check_execution_status(self):
        """Check execution status and handle completion."""
        if (
            st.session_state.session_data.execution_status
            == SessionExecutionStatus.COMPLETED
        ):
            # Add result message and reset status
            result = (
                st.session_state.session_data.execution_result or "No result available"
            )
            self.add_message(SessionMessage(role="assistant", content=result))
            st.session_state.session_data.execution_status = SessionExecutionStatus.IDLE
            st.session_state.session_data.progress_message = ""
            st.session_state.session_data.execution_result = None
            st.rerun()

        elif (
            st.session_state.session_data.execution_status
            == SessionExecutionStatus.ERROR
        ):
            # Add error message and reset status
            error_msg = (
                st.session_state.session_data.execution_error
                or "Unknown error occurred"
            )
            self.add_message(
                SessionMessage(role="assistant", content=f"❌ Error: {error_msg}")
            )
            st.session_state.session_data.execution_status = SessionExecutionStatus.IDLE
            st.session_state.session_data.progress_message = ""
            st.session_state.session_data.execution_error = None
            st.rerun()

        elif (
            st.session_state.session_data.execution_status
            == SessionExecutionStatus.CANCELLED
        ):
            # Add cancellation message and reset status
            self.add_message(
                SessionMessage(role="assistant", content="🚫 Execution was cancelled")
            )
            st.session_state.session_data.execution_status = SessionExecutionStatus.IDLE
            st.session_state.session_data.progress_message = ""
            st.rerun()

        elif (
            st.session_state.session_data.execution_status
            == SessionExecutionStatus.RUNNING
        ):
            # Schedule another check in a moment
            time.sleep(0.1)
            st.rerun()

    def cancel_execution(self):
        """Cancel the current execution."""
        with self._execution_lock:
            if (
                self._execution_thread
                and self._execution_thread.is_alive()
                and st.session_state.session_data.execution_status
                == SessionExecutionStatus.RUNNING
            ):
                self._cancel_flag.set()
                st.session_state.session_data.progress_message = (
                    "Cancelling execution..."
                )
                st.rerun()

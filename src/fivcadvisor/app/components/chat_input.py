import streamlit as st

from fivcadvisor.app.sessions import Session, SessionExecutionStatus


class ChatInput(object):
    def __init__(self, session: Session):
        self.session = session

    def render(self):
        # Determine placeholder text based on execution status
        if self.session.execution_status == SessionExecutionStatus.RUNNING:
            placeholder = "Agent is working... Please wait"
        elif self.session.is_processing:
            placeholder = "Processing your request..."
        else:
            placeholder = "Ask me anything..."

        user_query = st.chat_input(placeholder, disabled=self.session.is_processing)
        if not user_query:
            return

        # Immediately set processing state to disable input and set the query
        self.session.ask(user_query)
        # Force immediate re-render to show disabled state
        st.rerun()

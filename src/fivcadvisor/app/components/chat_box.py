import streamlit as st
from fivcadvisor.app.sessions import Session, SessionExecutionStatus


class ChatBox(object):
    def __init__(self, session: Session):
        self.session = session

    def render(self):
        # Header
        st.header(":sunglasses: :blue[FivAdvisor] chills", divider="blue")

        # Display messages
        for message in self.session.get_messages():
            if message.role == "user":
                st.chat_message("user").write(message.content)
            elif message.role == "assistant":
                st.chat_message("assistant").write(message.content)

        # Display execution status if running
        if self.session.execution_status == SessionExecutionStatus.RUNNING:
            with st.chat_message("assistant"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("🤖 Agent is working...")
                    if self.session.progress_message:
                        st.caption(self.session.progress_message)
                    st.progress(0.5)  # Indeterminate progress
                with col2:
                    if st.button("Cancel", key="cancel_execution", type="secondary"):
                        self.session.cancel_execution()

import streamlit as st

from fivcadvisor.app.sessions import Session


class ConfigPanel(object):
    def __init__(self, session: Session):
        self.session = session

    def render(self):
        st.header("FivcAdvisor")

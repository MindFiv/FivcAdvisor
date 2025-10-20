"""
Settings Page

Application settings and configuration.
"""

import streamlit as st

from .base import ViewBase, ViewNavigation


class SettingsView(ViewBase):
    """Settings view"""

    def __init__(self):
        super().__init__("Settings", "⚙️")

    @property
    def id(self) -> str:
        return "settings"

    def render(self, nav: "ViewNavigation"):
        """Render settings page"""
        """Render settings page"""

        st.title("⚙️ Settings")

        st.subheader("🤖 Model Configuration")

        col1, col2 = st.columns(2)
        with col1:
            _ = st.selectbox("Provider", ["OpenAI", "Ollama", "LiteLLM"], index=0)

        with col2:
            _ = st.text_input("Model", "gpt-4")

        st.divider()

        st.subheader("💾 Chat Configuration")

        # col1, col2 = st.columns(2)
        # with col1:
        #     if st.button("🗑️ 清理旧通知", use_container_width=True):
        #         st.success("已清理 7 天前的通知")
        #
        # with col2:
        #     if st.button("🔄 重置会话", use_container_width=True, type="secondary"):
        #         chat_session = st.session_state.chat_session
        #         chat_session.cleanup()
        #         st.success("会话已重置")
        #         st.rerun()

        st.divider()

        # Save settings
        if st.button("💾 Save", type="primary", use_container_width=False):
            # Save to session_state

            st.success("✅ Saved！")

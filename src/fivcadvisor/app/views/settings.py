"""
Settings Page

Application settings and configuration.
"""

import streamlit as st


def render():
    """Render settings page"""

    st.title("⚙️ 系统设置")

    st.subheader("🤖 模型配置")

    col1, col2 = st.columns(2)
    with col1:
        model_provider = st.selectbox(
            "LLM 提供商", ["OpenAI", "Ollama", "LiteLLM"], index=0
        )

    with col2:
        model_name = st.text_input("模型名称", "gpt-4")

    st.divider()

    st.subheader("🔧 任务配置")

    col1, col2 = st.columns(2)
    with col1:
        complexity_threshold = st.slider(
            "复杂度阈值",
            min_value=1,
            max_value=10,
            value=7,
            help="评分 >= 此值时建议使用复杂流程",
        )

    with col2:
        max_subtasks = st.number_input(
            "最大子任务数",
            min_value=1,
            max_value=20,
            value=5,
            help="复杂任务最多分解为多少个子任务",
        )

    st.divider()

    st.subheader("💾 会话管理")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清理旧通知", use_container_width=True):
            from fivcadvisor.workflows import NotificationManager

            chat_session = st.session_state.chat_session
            notification_manager = NotificationManager()
            notification_manager.clear_old_notifications(
                chat_session.session_id, days=7
            )
            st.success("已清理 7 天前的通知")

    with col2:
        if st.button("🔄 重置会话", use_container_width=True, type="secondary"):
            chat_session = st.session_state.chat_session
            chat_session.cleanup()
            st.success("会话已重置")
            st.rerun()

    st.divider()

    # Save settings
    if st.button("💾 保存设置", type="primary", use_container_width=True):
        # Save to session_state
        st.session_state.settings = {
            "model_provider": model_provider,
            "model_name": model_name,
            "complexity_threshold": complexity_threshold,
            "max_subtasks": max_subtasks,
        }
        st.success("✅ 设置已保存！")

    # Display current settings
    if "settings" in st.session_state:
        st.divider()
        st.subheader("📋 当前设置")
        st.json(st.session_state.settings)

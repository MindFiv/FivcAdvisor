"""
FivcAdvisor Side Bar Component

A reusable sidebar component for FivcAdvisor with configuration and chat controls.
"""

from typing import Dict, Any, List, Optional, Callable
import streamlit as st


class SideBar:
    """
    A reusable sidebar component for FivcAdvisor applications.

    This component encapsulates all sidebar-related functionality including:
    - Configuration controls (graph type, verbose mode)
    - Graph information display
    - Chat controls (clear chat, example queries)
    - Custom sections and controls
    """

    def __init__(
        self,
        session_key_prefix: str = "sidebar",
        title: str = "⚙️ Configuration",
        show_graph_info: bool = True,
        show_chat_controls: bool = True,
    ):
        """
        Initialize the sidebar component.

        Args:
            session_key_prefix: Prefix for session state keys
            title: Title for the sidebar
            show_graph_info: Whether to show graph information section
            show_chat_controls: Whether to show chat control section
        """
        self.session_key_prefix = session_key_prefix
        self.title = title
        self.show_graph_info = show_graph_info
        self.show_chat_controls = show_chat_controls

    def render(
        self,
        available_graphs: Dict[str, str],
        current_graph_type: str,
        current_verbose: bool,
        clear_chat_callback: Optional[Callable[[], None]] = None,
        example_queries_callback: Optional[Callable[[], List[str]]] = None,
        handle_example_query_callback: Optional[
            Callable[[str, str, bool], None]
        ] = None,
        show_examples: bool = True,
        max_examples: int = 4,
        custom_sections: Optional[List[Callable[[], None]]] = None,
    ) -> Dict[str, Any]:
        """
        Render the complete sidebar.

        Args:
            available_graphs: Dictionary of available graph types and descriptions
            current_graph_type: Currently selected graph type
            current_verbose: Current verbose mode setting
            clear_chat_callback: Callback function to clear chat
            example_queries_callback: Callback to get example queries
            handle_example_query_callback: Callback to handle example query selection
            show_examples: Whether to show example queries
            max_examples: Maximum number of example queries to show
            custom_sections: List of custom section render functions

        Returns:
            Dictionary with updated configuration values
        """
        with st.sidebar:
            # Sidebar title
            st.header(self.title)

            # Configuration section
            config = self._render_configuration_section(
                available_graphs, current_graph_type, current_verbose
            )

            # Graph information section
            if self.show_graph_info:
                self._render_graph_info_section(available_graphs, config["graph_type"])

            # Custom sections
            if custom_sections:
                for section_func in custom_sections:
                    st.markdown("---")
                    section_func()

            # Chat controls section
            if self.show_chat_controls:
                self._render_chat_controls_section(
                    config["graph_type"],
                    config["verbose"],
                    clear_chat_callback,
                    example_queries_callback,
                    handle_example_query_callback,
                    show_examples,
                    max_examples,
                )

            return config

    def _render_configuration_section(
        self,
        available_graphs: Dict[str, str],
        current_graph_type: str,
        current_verbose: bool,
    ) -> Dict[str, Any]:
        """Render the configuration section."""
        # Graph type selection
        graph_options = [(f"{k.title()} - {v}", k) for k, v in available_graphs.items()]
        graph_labels = [option[0] for option in graph_options]
        graph_values = [option[1] for option in graph_options]

        selected_index = 0
        if current_graph_type in graph_values:
            selected_index = graph_values.index(current_graph_type)

        selected_label = st.selectbox(
            "Graph Type",
            graph_labels,
            index=selected_index,
            help="Select the processing strategy",
            key=f"{self.session_key_prefix}_graph_type",
        )
        selected_graph_type = graph_values[graph_labels.index(selected_label)]

        # Verbose mode
        verbose_mode = st.checkbox(
            "Verbose Mode",
            value=current_verbose,
            help="Show detailed processing information",
            key=f"{self.session_key_prefix}_verbose",
        )

        return {
            "graph_type": selected_graph_type,
            "verbose": verbose_mode,
        }

    def _render_graph_info_section(
        self, available_graphs: Dict[str, str], graph_type: str
    ):
        """Render the graph information section."""
        st.markdown("---")
        st.subheader("📊 Graph Information")
        st.info(f"**{graph_type.title()} Graph**\n\n{available_graphs[graph_type]}")

    def _render_chat_controls_section(
        self,
        graph_type: str,
        verbose: bool,
        clear_chat_callback: Optional[Callable[[], None]],
        example_queries_callback: Optional[Callable[[], List[str]]],
        handle_example_query_callback: Optional[Callable[[str, str, bool], None]],
        show_examples: bool,
        max_examples: int,
    ):
        """Render the chat controls section."""
        st.markdown("---")

        # Clear chat button
        if clear_chat_callback:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                clear_chat_callback()
                st.rerun()

        # Example queries
        if show_examples and example_queries_callback and handle_example_query_callback:
            self._render_example_queries_section(
                graph_type,
                verbose,
                example_queries_callback,
                handle_example_query_callback,
                max_examples,
            )

    def _render_example_queries_section(
        self,
        graph_type: str,
        verbose: bool,
        example_queries_callback: Callable[[], List[str]],
        handle_example_query_callback: Callable[[str, str, bool], None],
        max_examples: int,
    ):
        """Render the example queries section."""
        st.subheader("💡 Example Queries")
        example_queries = example_queries_callback()

        for i, query in enumerate(example_queries[:max_examples]):
            if st.button(
                f"📝 {query[:30]}...",
                key=f"{self.session_key_prefix}_example_{i}",
                use_container_width=True,
            ):
                handle_example_query_callback(query, graph_type, verbose)


class ChatSideBar(SideBar):
    """
    A specialized sidebar component for chat applications.

    This extends the base SideBar with chat-specific functionality.
    """

    def __init__(self, session_key_prefix: str = "chat_sidebar"):
        """Initialize the chat sidebar."""
        super().__init__(
            session_key_prefix=session_key_prefix,
            title="⚙️ Configuration",
            show_graph_info=True,
            show_chat_controls=True,
        )

    def render_for_chat_box(
        self,
        available_graphs: Dict[str, str],
        current_graph_type: str,
        current_verbose: bool,
        chat_box,  # ChatBox instance
        show_examples: bool = True,
        max_examples: int = 4,
    ) -> Dict[str, Any]:
        """
        Render sidebar specifically for ChatBox integration.

        Args:
            available_graphs: Dictionary of available graph types
            current_graph_type: Currently selected graph type
            current_verbose: Current verbose mode setting
            chat_box: ChatBox instance for callbacks
            show_examples: Whether to show example queries
            max_examples: Maximum number of example queries to show

        Returns:
            Dictionary with updated configuration values
        """
        return self.render(
            available_graphs=available_graphs,
            current_graph_type=current_graph_type,
            current_verbose=current_verbose,
            clear_chat_callback=chat_box.clear_chat,
            example_queries_callback=chat_box.get_example_queries_callback,
            handle_example_query_callback=chat_box._handle_example_query,
            show_examples=show_examples,
            max_examples=max_examples,
        )


def create_default_sidebar(session_key_prefix: str = "default_sidebar") -> SideBar:
    """
    Create a default sidebar with standard settings.

    Args:
        session_key_prefix: Prefix for session state keys

    Returns:
        Configured SideBar instance
    """
    return SideBar(session_key_prefix=session_key_prefix)


def create_chat_sidebar(session_key_prefix: str = "chat_sidebar") -> ChatSideBar:
    """
    Create a chat-specific sidebar with standard settings.

    Args:
        session_key_prefix: Prefix for session state keys

    Returns:
        Configured ChatSideBar instance
    """
    return ChatSideBar(session_key_prefix=session_key_prefix)

"""
MCP Settings Page

Provides configuration interface for Model Context Protocol (MCP) servers.

This module implements the MCP settings view for the FivcAdvisor web interface,
allowing users to configure and manage MCP server connections. The view handles:
- Displaying configured MCP servers
- Adding new command-based or URL-based servers
- Editing MCP configuration in YAML format
- Testing MCP server connectivity

The MCP settings view uses the default_mcp_config from app.utils for persistence
and provides both UI-based and direct YAML editing interfaces for flexibility.
"""

import streamlit as st
import yaml

from fivcadvisor.app.views.base import ViewBase, ViewNavigation
from fivcadvisor.app.utils import default_mcp_config


class MCPSettingView(ViewBase):
    """MCP Setting view

    Manages Model Context Protocol (MCP) server configuration and connectivity.
    Provides interfaces for adding, editing, and testing MCP servers.
    """

    # UI Labels and Messages
    TITLE = "MCP Settings"
    ICON = "🔗"
    VIEW_ID = "mcp_setting"

    # Tab names
    TAB_MANAGE = "📋 Manage Servers"
    TAB_YAML = "✏️ Edit YAML"
    TAB_HELP = "ℹ️ Help"

    # Section headers
    HEADER_CONFIGURED = "📋 Configured Servers"
    HEADER_ADD_SERVER = "➕ Add New Server"
    HEADER_TEST = "🧪 Test Server"
    HEADER_YAML_EDIT = "✏️ Edit YAML Configuration"
    HEADER_HELP = "📚 MCP Configuration Guide"
    HEADER_WHAT_IS_MCP = "🔗 What is MCP?"
    HEADER_CONFIG_TYPES = "📋 Configuration Types"
    HEADER_EXAMPLES = "💡 Popular Examples"
    HEADER_BEST_PRACTICES = "✨ Best Practices"
    HEADER_CONFIG_FILE = "📄 Configuration File"

    # Server type labels
    TYPE_COMMAND = "Command"
    TYPE_URL = "URL"
    TYPE_COMMAND_LABEL = "**Type:** `Command`"
    TYPE_URL_LABEL = "**Type:** `URL`"

    # Field labels
    LABEL_SERVER_NAME = "Server Name"
    LABEL_SERVER_TYPE = "Server Type"
    LABEL_COMMAND = "Command"
    LABEL_ARGS = "Arguments (one per line)"
    LABEL_ENV = "Environment Variables (optional)"
    LABEL_SERVER_URL = "Server URL"
    LABEL_YAML_CONFIG = "MCP Configuration (YAML)"

    # Placeholders
    PLACEHOLDER_SERVER_NAME = "e.g., playwright, sequential-thinking"
    PLACEHOLDER_COMMAND = "e.g., npx, python"
    PLACEHOLDER_ARGS = "@playwright/mcp@latest\n--option value"
    PLACEHOLDER_ENV = "KEY1=value1\nKEY2=value2"
    PLACEHOLDER_URL = "http://localhost:8000"

    # Help texts
    HELP_SERVER_NAME = "Unique identifier for this MCP server"
    HELP_SERVER_TYPE = "Choose how to connect to the MCP server"
    HELP_COMMAND = "The command to execute"
    HELP_ARGS = "Command line arguments, one per line"
    HELP_ENV = "Environment variables, one per line in KEY=value format"
    HELP_SERVER_URL = "The URL of the MCP server"
    HELP_YAML = "Edit the MCP configuration directly in YAML format"

    # Button labels
    BTN_ADD_SERVER = "✅ Add Server"
    BTN_SAVE_CONFIG = "💾 Save Configuration"
    BTN_RESET = "🔄 Reset"
    BTN_COPY = "📋 Copy"
    BTN_RUN_TEST = "▶️ Run Test"
    BTN_DELETE = "🗑️ Delete"

    # Messages
    MSG_NO_SERVERS = "🚀 No MCP servers configured yet. Add your first server below!"
    MSG_CONFIGURE_COMMAND = "**Configure Command Server**"
    MSG_CONFIGURE_URL = "**Configure URL Server**"
    MSG_TEST_DESCRIPTION = (
        "Validate your MCP configuration and check server connectivity."
    )
    MSG_YAML_DESCRIPTION = """
        Edit your MCP configuration directly in YAML format. This is useful for:
        - Bulk updates to multiple servers
        - Advanced configuration options
        - Direct file editing
        """
    MSG_COPY_CLIPBOARD = "Configuration copied to clipboard (in your browser)"

    # Error messages
    ERR_SERVER_NAME_REQUIRED = "❌ Server name is required"
    ERR_SERVER_EXISTS = "❌ Server '{name}' already exists"
    ERR_COMMAND_REQUIRED = "❌ Command is required"
    ERR_URL_REQUIRED = "❌ URL is required"
    ERR_INVALID_CONFIG = "❌ Invalid configuration for '{name}'"
    ERR_DELETED = "✅ Deleted '{name}'"
    ERR_ADDED = "✅ Added server '{name}'"
    ERR_YAML_PARSE = "❌ YAML parsing error: {error}"
    ERR_GENERAL = "❌ Error: {error}"
    ERR_TEST_FAILED = "❌ Error testing configuration: {error}"

    # Success messages
    SUCCESS_SAVED = "✅ Configuration saved successfully!"
    SUCCESS_VALID = "✅ Configuration is valid! Found {count} clients"

    # Warning messages
    WARN_CONFIG_ERRORS = "⚠️ Configuration has errors:"

    # Config keys
    KEY_COMMAND = "command"
    KEY_URL = "url"
    KEY_ARGS = "args"
    KEY_ENV = "env"

    # Divider colors
    DIVIDER_BLUE = "blue"
    DIVIDER_GREEN = "green"
    DIVIDER_ORANGE = "orange"

    # Grid layout
    COLS_PER_ROW = 2
    YAML_HEIGHT = 400
    ARGS_HEIGHT = 80
    ENV_HEIGHT = 80

    # Help tab content
    HELP_WHAT_IS_MCP = """
        **Model Context Protocol (MCP)** is a protocol for connecting AI models to external tools and data sources.
        It enables seamless integration of custom tools and services with your AI assistant.
        """

    HELP_COMMAND_SERVER_TITLE = "#### 🖥️ Command-based Server"
    HELP_COMMAND_SERVER_DESC = "Runs a local command to start the MCP server:"
    HELP_COMMAND_SERVER_EXAMPLE = """playwright:
  command: "npx"
  args:
    - "@playwright/mcp@latest"
  env:
    DEBUG: "true"
"""

    HELP_URL_SERVER_TITLE = "#### 🌐 URL-based Server"
    HELP_URL_SERVER_DESC = "Connects to a remote MCP server via HTTP:"
    HELP_URL_SERVER_EXAMPLE = """remote-server:
  url: "http://localhost:8000"
"""

    HELP_EXAMPLE_PLAYWRIGHT_TITLE = "**Browser Automation with Playwright**"
    HELP_EXAMPLE_PLAYWRIGHT = """playwright:
  command: "npx"
  args:
    - "@playwright/mcp@latest"
"""

    HELP_EXAMPLE_SEQUENTIAL_TITLE = "**Sequential Thinking Server**"
    HELP_EXAMPLE_SEQUENTIAL = """sequential-thinking:
  command: "npx"
  args:
    - "-y"
    - "@modelcontextprotocol/server-sequential-thinking"
"""

    HELP_EXAMPLE_PYTHON_TITLE = "**Custom Python Script**"
    HELP_EXAMPLE_PYTHON = """custom-tool:
  command: "python"
  args:
    - "/path/to/server.py"
  env:
    PYTHONPATH: "/path/to/lib"
"""

    HELP_CONFIG_LOCATION = "**Location:** `mcp.yml`"
    HELP_CONFIG_STATUS = "**Status:** ✅ Managed by application"

    def __init__(self):
        super().__init__(self.TITLE, self.ICON)

    @property
    def id(self) -> str:
        """Unique identifier for this view."""
        return self.VIEW_ID

    def render(self, nav: "ViewNavigation"):
        """Render MCP settings page.

        Args:
            nav (ViewNavigation): Navigation instance for page management.
        """
        st.title(self.display_title)

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs([self.TAB_MANAGE, self.TAB_YAML, self.TAB_HELP])

        with tab1:
            self._render_manage_servers_tab()

        with tab2:
            self._render_edit_yaml_tab()

        with tab3:
            self._render_help_tab()

    def _render_manage_servers_tab(self):
        """Render the manage servers tab."""
        servers = default_mcp_config.list()

        # Display current servers section
        if servers:
            st.subheader(self.HEADER_CONFIGURED, divider=self.DIVIDER_BLUE)

            # Create expanders for each server
            for name in servers:
                self._render_server_expander(name)
        else:
            st.info(self.MSG_NO_SERVERS)

        st.divider()

        # Add new server section and Test configuration in two columns
        col_add, col_test = st.columns(2)

        with col_add:
            st.subheader(self.HEADER_ADD_SERVER, divider=self.DIVIDER_GREEN)

            col1, col2 = st.columns([2, 1])
            with col1:
                server_name = st.text_input(
                    self.LABEL_SERVER_NAME,
                    placeholder=self.PLACEHOLDER_SERVER_NAME,
                    help=self.HELP_SERVER_NAME,
                )
            with col2:
                server_type = st.selectbox(
                    self.LABEL_SERVER_TYPE,
                    [self.TYPE_COMMAND, self.TYPE_URL],
                    help=self.HELP_SERVER_TYPE,
                )

            self._render_add_server_form(server_name, server_type)

        with col_test:
            st.subheader(self.HEADER_TEST, divider=self.DIVIDER_ORANGE)
            st.write(self.MSG_TEST_DESCRIPTION)
            if st.button(self.BTN_RUN_TEST, type="primary", use_container_width=True):
                self._test_mcp_configuration()

    def _render_server_expander(self, name: str):
        """Render an expander for a server configuration.

        Args:
            name (str): Server name
        """
        settings = default_mcp_config.get(name)
        if not settings:
            return

        # Determine server type for display
        if self.KEY_COMMAND in settings:
            server_type_label = "🖥️ Command"
        elif self.KEY_URL in settings:
            server_type_label = "🌐 URL"
        else:
            server_type_label = "❓ Unknown"

        # Create expander with server name and type
        with st.expander(f"{self.ICON} {name} ({server_type_label})", expanded=False):
            # Header with delete button
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"### {name}")
            with col2:
                pass  # Spacer for alignment
            with col3:
                # Styled delete button with confirmation
                if st.button(
                    self.BTN_DELETE,
                    key=f"delete_{name}",
                    help="Delete this server configuration",
                    use_container_width=True,
                ):
                    # Show confirmation dialog
                    st.warning(f"⚠️ Are you sure you want to delete **{name}**?")
                    col_confirm1, col_confirm2 = st.columns(2)
                    with col_confirm1:
                        if st.button(
                            "✅ Confirm Delete",
                            key=f"confirm_delete_{name}",
                            use_container_width=True,
                        ):
                            default_mcp_config.delete(name)
                            default_mcp_config.save()
                            st.success(self.ERR_DELETED.format(name=name))
                            st.rerun()
                    with col_confirm2:
                        if st.button(
                            "❌ Cancel",
                            key=f"cancel_delete_{name}",
                            use_container_width=True,
                        ):
                            st.rerun()

            st.divider()

            # Server details
            if self.KEY_COMMAND in settings:
                st.markdown(self.TYPE_COMMAND_LABEL)
                st.markdown(f"**Command:** `{settings[self.KEY_COMMAND]}`")
                if self.KEY_ARGS in settings:
                    args_str = " ".join(settings[self.KEY_ARGS])
                    st.markdown(f"**Arguments:** `{args_str}`")
                if self.KEY_ENV in settings:
                    env_items = ", ".join(
                        [f"{k}={v}" for k, v in settings[self.KEY_ENV].items()]
                    )
                    st.markdown(f"**Environment:** `{env_items}`")
            elif self.KEY_URL in settings:
                st.markdown(self.TYPE_URL_LABEL)
                st.markdown(f"**URL:** `{settings[self.KEY_URL]}`")

    def _render_add_server_form(self, server_name: str, server_type: str):
        """Render form for adding a new server.

        Args:
            server_name (str): Server name
            server_type (str): Server type ("Command" or "URL")
        """
        if server_type == self.TYPE_COMMAND:
            st.markdown(self.MSG_CONFIGURE_COMMAND)
            command = st.text_input(
                self.LABEL_COMMAND,
                placeholder=self.PLACEHOLDER_COMMAND,
                help=self.HELP_COMMAND,
            )
            args_input = st.text_area(
                self.LABEL_ARGS,
                placeholder=self.PLACEHOLDER_ARGS,
                height=self.ARGS_HEIGHT,
                help=self.HELP_ARGS,
            )
            env_input = st.text_area(
                self.LABEL_ENV,
                placeholder=self.PLACEHOLDER_ENV,
                height=self.ENV_HEIGHT,
                help=self.HELP_ENV,
            )

            if st.button(self.BTN_ADD_SERVER, type="primary", use_container_width=True):
                self._add_server(
                    server_name, self.KEY_COMMAND, command, args_input, env_input
                )
        else:  # URL type
            st.markdown(self.MSG_CONFIGURE_URL)
            url = st.text_input(
                self.LABEL_SERVER_URL,
                placeholder=self.PLACEHOLDER_URL,
                help=self.HELP_SERVER_URL,
            )

            if st.button(self.BTN_ADD_SERVER, type="primary", use_container_width=True):
                self._add_server(server_name, self.KEY_URL, url)

    def _render_edit_yaml_tab(self):
        """Render the edit YAML tab."""
        st.subheader(self.HEADER_YAML_EDIT, divider=self.DIVIDER_BLUE)

        st.markdown(self.MSG_YAML_DESCRIPTION)

        # Convert current configs to YAML
        current_config = {}
        for name in default_mcp_config.list():
            config_value = default_mcp_config.get(name)
            # Convert ToolsConfigValue (dict subclass) to regular dict for YAML serialization
            current_config[name] = dict(config_value) if config_value else {}

        yaml_content = yaml.safe_dump(current_config, default_flow_style=False)

        edited_yaml = st.text_area(
            self.LABEL_YAML_CONFIG,
            value=yaml_content,
            height=self.YAML_HEIGHT,
            help=self.HELP_YAML,
        )

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button(
                self.BTN_SAVE_CONFIG, type="primary", use_container_width=True
            ):
                try:
                    new_config = yaml.safe_load(edited_yaml) or {}

                    # Validate and save each config
                    for name, cfg in new_config.items():
                        if not default_mcp_config.set(name, cfg):
                            st.error(self.ERR_INVALID_CONFIG.format(name=name))
                            return

                    default_mcp_config.save()
                    st.success(self.SUCCESS_SAVED)
                    st.rerun()
                except yaml.YAMLError as e:
                    st.error(self.ERR_YAML_PARSE.format(error=e))
                except Exception as e:
                    st.error(self.ERR_GENERAL.format(error=e))

        with col2:
            if st.button(self.BTN_RESET, use_container_width=True):
                st.rerun()

        with col3:
            if st.button(self.BTN_COPY, use_container_width=True):
                st.info(self.MSG_COPY_CLIPBOARD)

    def _render_help_tab(self):
        """Render the help tab with MCP configuration documentation."""
        st.subheader(self.HEADER_HELP, divider=self.DIVIDER_GREEN)

        # What is MCP section
        with st.container(border=True):
            st.markdown(f"### {self.HEADER_WHAT_IS_MCP}")
            st.markdown(self.HELP_WHAT_IS_MCP)

        st.divider()

        # Configuration Types section
        st.markdown(f"### {self.HEADER_CONFIG_TYPES}")

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown(self.HELP_COMMAND_SERVER_TITLE)
                st.markdown(self.HELP_COMMAND_SERVER_DESC)
                st.code(self.HELP_COMMAND_SERVER_EXAMPLE, language="yaml")

        with col2:
            with st.container(border=True):
                st.markdown(self.HELP_URL_SERVER_TITLE)
                st.markdown(self.HELP_URL_SERVER_DESC)
                st.code(self.HELP_URL_SERVER_EXAMPLE, language="yaml")

        st.divider()

        # Examples section
        st.markdown(f"### {self.HEADER_EXAMPLES}")

        example_tabs = st.tabs(["Playwright", "Sequential Thinking", "Python Script"])

        with example_tabs[0]:
            st.markdown(self.HELP_EXAMPLE_PLAYWRIGHT_TITLE)
            st.code(self.HELP_EXAMPLE_PLAYWRIGHT, language="yaml")

        with example_tabs[1]:
            st.markdown(self.HELP_EXAMPLE_SEQUENTIAL_TITLE)
            st.code(self.HELP_EXAMPLE_SEQUENTIAL, language="yaml")

        with example_tabs[2]:
            st.markdown(self.HELP_EXAMPLE_PYTHON_TITLE)
            st.code(self.HELP_EXAMPLE_PYTHON, language="yaml")

        st.divider()

        # Tips section
        st.markdown(f"### {self.HEADER_BEST_PRACTICES}")

        tips = [
            "🏷️ **Unique Names**: Server names must be unique identifiers",
            "🔍 **Executable Path**: Command must be executable from your system PATH",
            "📝 **Argument Order**: Arguments are passed in the order specified",
            "🌍 **Environment**: Variables are merged with system environment",
            "✅ **Validation**: Use the Test Configuration button to validate your setup",
        ]

        for tip in tips:
            st.markdown(f"- {tip}")

        st.divider()

        # Configuration file info
        with st.container(border=True):
            st.markdown(f"### {self.HEADER_CONFIG_FILE}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(self.HELP_CONFIG_LOCATION)
            with col2:
                st.markdown(self.HELP_CONFIG_STATUS)

    def _add_server(self, server_name: str, server_type: str, *args):
        """Add a new server to configuration.

        Args:
            server_name (str): Server name
            server_type (str): Server type ("command" or "url")
            *args: Additional arguments (command, args_input, env_input for command type;
                   url for url type)
        """
        if not server_name:
            st.error(self.ERR_SERVER_NAME_REQUIRED)
            return

        if server_name in default_mcp_config.list():
            st.error(self.ERR_SERVER_EXISTS.format(name=server_name))
            return

        # Build configuration based on server type
        if server_type == self.KEY_COMMAND:
            command, args_input, env_input = args
            if not command:
                st.error(self.ERR_COMMAND_REQUIRED)
                return

            config = {self.KEY_COMMAND: command}

            if args_input.strip():
                config[self.KEY_ARGS] = [
                    arg.strip() for arg in args_input.strip().split("\n") if arg.strip()
                ]

            if env_input.strip():
                env_dict = {}
                for line in env_input.strip().split("\n"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_dict[key.strip()] = value.strip()
                if env_dict:
                    config[self.KEY_ENV] = env_dict
        else:  # url type
            url = args[0]
            if not url:
                st.error(self.ERR_URL_REQUIRED)
                return
            config = {self.KEY_URL: url}

        # Use ToolsConfig.set() which validates automatically
        if default_mcp_config.set(server_name, config):
            default_mcp_config.save()
            st.success(self.ERR_ADDED.format(name=server_name))
            st.rerun()
        else:
            st.error(self.ERR_INVALID_CONFIG.format(name=server_name))

    def _test_mcp_configuration(self):
        """Test MCP configuration and display results."""
        try:
            # Get MCP client from configuration
            mcp_client = default_mcp_config.get_mcp_client()
            errors = default_mcp_config.get_errors()

            if errors:
                st.warning(self.WARN_CONFIG_ERRORS)
                for error in errors:
                    st.write(f"- {error}")
            elif mcp_client is not None:
                # Count configured servers
                server_count = len(default_mcp_config.list())
                st.success(self.SUCCESS_VALID.format(count=server_count))
            else:
                st.info("No MCP servers configured")
        except Exception as e:
            st.error(self.ERR_TEST_FAILED.format(error=e))

from typing import List

import streamlit as st
from strands.types.tools import ToolResult, ToolUse


class ToolRenderer(object):
    def __init__(self):
        self.tool_begin = {}
        self.tool_end = {}
        self.is_rendered = False

    def begin(self, tool_use: ToolUse):
        if self.tool_begin:
            raise ValueError("Tool use already started")
        self.tool_begin = tool_use

    def end(self, tool_result: ToolResult):
        if not self.tool_begin:
            raise ValueError("Tool use not started")
        if self.tool_end:
            raise ValueError("Tool result already ended")

        if tool_result.get("toolUseId") != self.tool_begin.get("toolUseId"):
            raise ValueError("Tool use ID mismatch")

        self.tool_end = tool_result

    @property
    def is_complete(self):
        return bool(self.tool_begin) and bool(self.tool_end)

    def render(self, force=True):
        """Render a tool use block in a user-friendly way."""
        if not self.is_complete:
            return

        if not force and self.is_rendered:
            return

        # Mark as is_rendered
        self.is_rendered = True

        tool_use_block = self.tool_begin
        tool_result_block = self.tool_end

        try:
            tool_name = tool_use_block.get("name", "Unknown Tool")
            tool_id = tool_use_block.get("toolUseId", "")
            tool_input = tool_use_block.get("input", {})

            # Extract tool result information
            tool_result_id = tool_result_block.get("toolUseId", "")
            tool_content = tool_result_block.get("content", "")
            is_error = tool_result_block.get("status", "") == "error"

            # Create an expander with the tool name and a tool icon
            with st.expander(f"🔧 **{tool_name}**", expanded=False):
                if is_error:
                    st.error("Tool executed with error")
                else:
                    st.success("Tool executed successfully")

                # Show tool ID if available
                if tool_id:
                    st.caption(f"Tool ID: `{tool_id}`")

                # Show tool input parameters
                if tool_input:
                    st.caption("Parameters:")
                    # Use st.json for nice formatting of the input parameters
                    st.json(tool_input)
                else:
                    st.info("No parameters provided")

                # Show tool result
                st.caption("Result:")

                if tool_content:
                    # Try to display content in a user-friendly way
                    if isinstance(tool_content, (dict, list)):
                        st.json(tool_content)
                    else:
                        # Display as code block for better formatting
                        st.code(str(tool_content), language="text")
                else:
                    st.info("No result content")

                # Show result ID if different from tool use ID
                if tool_result_id and tool_result_id != tool_id:
                    st.caption(f"Result ID: `{tool_result_id}`")

        except Exception as e:
            # Fallback rendering in case of any errors
            st.error(f"Error rendering tool use: {str(e)}")
            st.json({"tool_use": tool_use_block, "tool_result": tool_result_block})


class ToolsRenderer(object):
    def __init__(self):
        self.tool_traces: List[ToolRenderer] = [ToolRenderer()]

    def begin(self, message: ToolUse):
        tool_trace = self.tool_traces[-1]
        if tool_trace.is_complete:
            tool_trace = ToolRenderer()
            self.tool_traces.append(tool_trace)
        tool_trace.begin(message)

    def end(self, message: ToolResult):
        tool_trace = self.tool_traces[-1]
        if tool_trace.is_complete:
            tool_trace = ToolRenderer()
            self.tool_traces.append(tool_trace)
        tool_trace.end(message)

    def render(self, force=False):
        for tool_trace in self.tool_traces:
            if tool_trace.is_complete:
                tool_trace.render(force=force)


class ToolCallback(object):
    def __init__(self, placeholder):
        self.tool_traces = ToolsRenderer()
        self.placeholder = placeholder

    def __call__(self, message: ToolUse | ToolResult):
        if "toolUse" in message:
            self.tool_traces.begin(message["toolUse"])

        elif "toolResult" in message:
            self.tool_traces.end(message["toolResult"])

        # Clear the placeholder and re-render all traces
        self.placeholder.empty()
        with self.placeholder.container():
            self.tool_traces.render(force=True)

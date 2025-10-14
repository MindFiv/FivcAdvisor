#!/usr/bin/env python3
"""
Tests for chat_message component functionality.

Tests the chat message rendering functions:
- render() with different runtime states
- _render_message() with message content
- _render_stream() with streaming text
- _parse_think_tags() with various inputs
"""

import pytest
from unittest.mock import Mock
from fivcadvisor.app.components import chat_message
from fivcadvisor.agents.types import AgentsRuntime


class TestRenderFunction:
    """Test the main render() function."""

    def test_render_with_query_only(self):
        """Test rendering runtime with only query (no response yet)."""
        mock_placeholder = Mock()
        mock_user_msg = Mock()
        mock_assistant_msg = Mock()
        mock_placeholder.chat_message.side_effect = [mock_user_msg, mock_assistant_msg]

        runtime = AgentsRuntime(
            agent_id="test-agent",
            query="What is the weather?",
            streaming_text="",
        )

        chat_message.render(mock_placeholder, runtime)

        # Should create user and assistant messages
        assert mock_placeholder.chat_message.call_count == 2
        mock_placeholder.chat_message.assert_any_call("user")
        mock_placeholder.chat_message.assert_any_call("assistant")

        # User message should display query
        mock_user_msg.text.assert_called_once_with("What is the weather?")

    def test_render_with_completed_message(self):
        """Test rendering runtime with completed message."""
        mock_placeholder = Mock()
        mock_user_msg = Mock()
        mock_assistant_msg = Mock()
        mock_placeholder.chat_message.side_effect = [mock_user_msg, mock_assistant_msg]

        message = {
            "role": "assistant",
            "content": [{"text": "The weather is sunny."}],
        }

        runtime = AgentsRuntime(
            agent_id="test-agent",
            query="What is the weather?",
            message=message,
        )

        chat_message.render(mock_placeholder, runtime)

        # Should render completed message
        mock_assistant_msg.markdown.assert_called_once()
        call_args = mock_assistant_msg.markdown.call_args[0][0]
        assert "sunny" in call_args

    def test_render_with_streaming_text(self):
        """Test rendering runtime with streaming text."""
        mock_placeholder = Mock()
        mock_user_msg = Mock()
        mock_assistant_msg = Mock()
        mock_placeholder.chat_message.side_effect = [mock_user_msg, mock_assistant_msg]

        runtime = AgentsRuntime(
            agent_id="test-agent",
            query="Tell me a story",
            streaming_text="Once upon a time...",
        )

        chat_message.render(mock_placeholder, runtime)

        # Should render streaming text with loading indicator
        mock_assistant_msg.markdown.assert_called_once()
        call_args = mock_assistant_msg.markdown.call_args[0][0]
        assert "Once upon a time" in call_args
        assert "loading-dots" in call_args  # Loading indicator present

    def test_render_without_query(self):
        """Test rendering runtime without query (assistant-only message)."""
        mock_placeholder = Mock()
        mock_assistant_msg = Mock()
        mock_placeholder.chat_message.return_value = mock_assistant_msg

        runtime = AgentsRuntime(
            agent_id="test-agent",
            streaming_text="Thinking...",
        )

        chat_message.render(mock_placeholder, runtime)

        # Should only create assistant message
        mock_placeholder.chat_message.assert_called_once_with("assistant")


class TestRenderMessageFunction:
    """Test the _render_message() function."""

    def test_render_message_with_single_text_block(self):
        """Test rendering message with single text content block."""
        mock_placeholder = Mock()

        message = {
            "role": "assistant",
            "content": [{"text": "Hello, world!"}],
        }

        chat_message._render_message(mock_placeholder, message)

        mock_placeholder.markdown.assert_called_once()
        call_args = mock_placeholder.markdown.call_args[0][0]
        assert "Hello, world!" in call_args

    def test_render_message_with_multiple_text_blocks(self):
        """Test rendering message with multiple text content blocks."""
        mock_placeholder = Mock()

        message = {
            "role": "assistant",
            "content": [
                {"text": "First part."},
                {"text": "Second part."},
                {"text": "Third part."},
            ],
        }

        chat_message._render_message(mock_placeholder, message)

        # Should call markdown for each text block
        assert mock_placeholder.markdown.call_count == 3

    def test_render_message_with_think_tags(self):
        """Test rendering message with <think> tags."""
        mock_placeholder = Mock()

        message = {
            "role": "assistant",
            "content": [{"text": "<think>Processing...</think>The answer is 42."}],
        }

        chat_message._render_message(mock_placeholder, message)

        mock_placeholder.markdown.assert_called_once()
        call_args = mock_placeholder.markdown.call_args[0][0]
        # Think tags should be processed into styled HTML
        assert "think-container" in call_args
        assert "Processing..." in call_args
        assert "The answer is 42" in call_args

    def test_render_message_ignores_non_text_blocks(self):
        """Test rendering message ignores non-text content blocks."""
        mock_placeholder = Mock()

        message = {
            "role": "assistant",
            "content": [
                {"text": "Text content"},
                {"toolUse": {"name": "test_tool"}},  # Should be ignored
                {"image": {"url": "test.jpg"}},  # Should be ignored
            ],
        }

        chat_message._render_message(mock_placeholder, message)

        # Should only render the text block
        mock_placeholder.markdown.assert_called_once()

    def test_render_message_with_unsafe_html_enabled(self):
        """Test rendering message enables unsafe_allow_html."""
        mock_placeholder = Mock()

        message = {
            "role": "assistant",
            "content": [{"text": "Test"}],
        }

        chat_message._render_message(mock_placeholder, message)

        # Verify unsafe_allow_html is True
        call_kwargs = mock_placeholder.markdown.call_args[1]
        assert call_kwargs.get("unsafe_allow_html") is True


class TestRenderStreamFunction:
    """Test the _render_stream() function."""

    def test_render_stream_with_text(self):
        """Test rendering streaming text."""
        mock_placeholder = Mock()

        chat_message._render_stream(mock_placeholder, "Streaming response...")

        mock_placeholder.markdown.assert_called_once()
        call_args = mock_placeholder.markdown.call_args[0][0]
        assert "Streaming response..." in call_args
        assert "loading-dots" in call_args

    def test_render_stream_with_empty_text(self):
        """Test rendering with empty streaming text."""
        mock_placeholder = Mock()

        chat_message._render_stream(mock_placeholder, "")

        mock_placeholder.markdown.assert_called_once()
        call_args = mock_placeholder.markdown.call_args[0][0]
        # Should still have loading indicator
        assert "loading-dots" in call_args

    def test_render_stream_includes_css_animations(self):
        """Test rendering includes CSS for loading animations."""
        mock_placeholder = Mock()

        chat_message._render_stream(mock_placeholder, "Test")

        call_args = mock_placeholder.markdown.call_args[0][0]
        # Should include CSS styles
        assert "@keyframes" in call_args
        assert "pulse" in call_args
        assert "glow" in call_args

    def test_render_stream_processes_think_tags(self):
        """Test rendering processes think tags in streaming text."""
        mock_placeholder = Mock()

        chat_message._render_stream(
            mock_placeholder, "<think>Analyzing...</think>Result"
        )

        call_args = mock_placeholder.markdown.call_args[0][0]
        # Think tags should be processed
        assert "think-container" in call_args
        assert "Analyzing..." in call_args


class TestParseThinkTagsFunction:
    """Test the _parse_think_tags() function."""

    def test_parse_think_tags_with_single_tag(self):
        """Test parsing single think tag."""
        text = "Before <think>thinking content</think> after"
        result = chat_message._parse_think_tags(text)

        assert "think-container" in result
        assert "thinking content" in result
        assert "Before" in result
        assert "after" in result

    def test_parse_think_tags_with_multiple_tags(self):
        """Test parsing multiple think tags."""
        text = "<think>First thought</think> middle <think>Second thought</think> end"
        result = chat_message._parse_think_tags(text)

        # Count div elements with think-container class (not CSS definition)
        assert result.count('<div class="think-container">') == 2
        assert "First thought" in result
        assert "Second thought" in result
        assert "middle" in result

    def test_parse_think_tags_with_multiline_content(self):
        """Test parsing think tag with multiline content."""
        text = """<think>
        Line 1
        Line 2
        Line 3
        </think>"""
        result = chat_message._parse_think_tags(text)

        assert "think-container" in result
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_parse_think_tags_without_tags(self):
        """Test parsing text without think tags."""
        text = "Just regular text without any tags"
        result = chat_message._parse_think_tags(text)

        # Should return unchanged text
        assert result == text
        assert "think-container" not in result

    def test_parse_think_tags_includes_css_when_tags_present(self):
        """Test CSS styles are included when think tags are present."""
        text = "<think>content</think>"
        result = chat_message._parse_think_tags(text)

        # Should include CSS styles
        assert "<style>" in result
        assert ".think-container" in result
        assert "gradient" in result

    def test_parse_think_tags_no_css_when_no_tags(self):
        """Test CSS styles are not included when no think tags."""
        text = "No think tags here"
        result = chat_message._parse_think_tags(text)

        # Should not include CSS
        assert "<style>" not in result
        assert ".think-container" not in result

    def test_parse_think_tags_with_empty_content(self):
        """Test parsing think tag with empty content."""
        text = "<think></think>"
        result = chat_message._parse_think_tags(text)

        assert "think-container" in result
        # Should still create the container even if empty

    def test_parse_think_tags_preserves_html_in_content(self):
        """Test parsing preserves HTML content inside think tags."""
        text = "<think>Some <b>bold</b> text</think>"
        result = chat_message._parse_think_tags(text)

        assert "think-container" in result
        assert "<b>bold</b>" in result

    def test_parse_think_tags_with_nested_angle_brackets(self):
        """Test parsing handles nested angle brackets correctly."""
        text = "<think>x < y and y > z</think>"
        result = chat_message._parse_think_tags(text)

        assert "think-container" in result
        assert "x < y and y > z" in result


class TestIntegration:
    """Integration tests for chat_message module."""

    def test_full_render_flow_with_streaming(self):
        """Test complete render flow with streaming runtime."""
        mock_placeholder = Mock()
        mock_user_msg = Mock()
        mock_assistant_msg = Mock()
        mock_placeholder.chat_message.side_effect = [mock_user_msg, mock_assistant_msg]

        runtime = AgentsRuntime(
            agent_id="test-agent",
            query="Calculate 2+2",
            streaming_text="<think>Let me calculate...</think>The answer is 4",
        )

        chat_message.render(mock_placeholder, runtime)

        # Verify user message
        mock_user_msg.text.assert_called_once_with("Calculate 2+2")

        # Verify assistant message with think tags and loading
        mock_assistant_msg.markdown.assert_called_once()
        call_args = mock_assistant_msg.markdown.call_args[0][0]
        assert "think-container" in call_args
        assert "Let me calculate..." in call_args
        assert "The answer is 4" in call_args
        assert "loading-dots" in call_args

    def test_full_render_flow_with_completed_message(self):
        """Test complete render flow with completed message."""
        mock_placeholder = Mock()
        mock_user_msg = Mock()
        mock_assistant_msg = Mock()
        mock_placeholder.chat_message.side_effect = [mock_user_msg, mock_assistant_msg]

        message = {
            "role": "assistant",
            "content": [
                {"text": "<think>Processing query...</think>"},
                {"text": "Here is your answer."},
            ],
        }

        runtime = AgentsRuntime(
            agent_id="test-agent",
            query="Help me",
            message=message,
        )

        chat_message.render(mock_placeholder, runtime)

        # Verify both text blocks were rendered
        assert mock_assistant_msg.markdown.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

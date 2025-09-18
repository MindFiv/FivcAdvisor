"""
Unit tests for logger console output suppression functionality.

Tests the updated create_default_logger function to ensure proper
console output control when file logging is configured.
"""

import os
import tempfile
from unittest.mock import patch
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from fivcadvisor.logs import create_default_logger


class TestLoggerConsoleSuppression:
    """Test cases for logger console output suppression."""

    def test_file_only_logging_suppresses_console(self):
        """Test that file logging doesn't output to console by default."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            # Mock the settings to avoid configuration dependencies
            with patch("fivcadvisor.logs.settings.default_logger_config", {}):
                logger = create_default_logger(
                    name="test_file_only",
                    level="INFO",
                    file=log_file,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                )

                # Verify logger configuration
                assert (
                    logger.propagate is False
                ), "Logger should not propagate to parent loggers"
                assert len(logger.handlers) == 1, "Should have exactly one handler"
                assert isinstance(
                    logger.handlers[0], RotatingFileHandler
                ), "Should have file handler"

                # Test logging
                logger.info("Test message")
                logger.warning("Test warning")

                # Verify file contains messages
                with open(log_file, "r") as f:
                    content = f.read()

                assert "Test message" in content, "Log file should contain the message"
                assert "Test warning" in content, "Log file should contain the warning"
                assert len(content.splitlines()) == 2, "Should have 2 log lines"

        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_file_and_console_logging_when_explicitly_enabled(self):
        """Test that both file and console logging work when console=True."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            with patch("fivcadvisor.logs.settings.default_logger_config", {}):
                logger = create_default_logger(
                    name="test_file_and_console",
                    level="INFO",
                    file=log_file,
                    console=True,  # Explicitly enable console
                    format="%(levelname)s - %(message)s",
                )

                # Verify logger configuration
                assert (
                    logger.propagate is True
                ), "Logger should propagate when console is enabled"
                assert len(logger.handlers) == 2, "Should have two handlers"

                handler_types = [type(h).__name__ for h in logger.handlers]
                assert (
                    "RotatingFileHandler" in handler_types
                ), "Should have file handler"
                assert "StreamHandler" in handler_types, "Should have console handler"

        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_console_only_logging_default_behavior(self):
        """Test console-only logging when no file is specified."""
        with patch("fivcadvisor.logs.settings.default_logger_config", {}):
            logger = create_default_logger(
                name="test_console_only",
                level="INFO",
                format="%(levelname)s - %(message)s",
            )

            # Verify logger configuration
            assert logger.propagate is True, "Logger should propagate for console-only"
            assert len(logger.handlers) == 1, "Should have exactly one handler"
            assert isinstance(
                logger.handlers[0], StreamHandler
            ), "Should have console handler"

    def test_handlers_are_cleared_on_recreation(self):
        """Test that existing handlers are cleared when recreating logger."""
        with patch("fivcadvisor.logs.settings.default_logger_config", {}):
            # Create logger first time
            logger1 = create_default_logger(name="test_handler_clearing", level="INFO")
            initial_handler_count = len(logger1.handlers)

            # Create same logger again
            logger2 = create_default_logger(name="test_handler_clearing", level="INFO")

            # Should be the same logger instance but handlers should be reset
            assert logger1 is logger2, "Should be the same logger instance"
            assert (
                len(logger2.handlers) == initial_handler_count
            ), "Handler count should be consistent"

    def test_console_parameter_overrides_file_default(self):
        """Test that console parameter overrides the default file behavior."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            with patch("fivcadvisor.logs.settings.default_logger_config", {}):
                # Test console=False with file (should be file-only)
                logger1 = create_default_logger(
                    name="test_console_override_false", file=log_file, console=False
                )
                assert len(logger1.handlers) == 1
                assert isinstance(logger1.handlers[0], RotatingFileHandler)
                assert logger1.propagate is False

                # Test console=True with file (should be both)
                logger2 = create_default_logger(
                    name="test_console_override_true", file=log_file, console=True
                )
                assert len(logger2.handlers) == 2
                handler_types = [type(h).__name__ for h in logger2.handlers]
                assert "RotatingFileHandler" in handler_types
                assert "StreamHandler" in handler_types
                assert logger2.propagate is True

        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_logger_level_setting(self):
        """Test that logger level is properly set."""
        with patch("fivcadvisor.logs.settings.default_logger_config", {}):
            logger = create_default_logger(name="test_level", level="DEBUG")

            # Note: getLogger().setLevel() expects integer or string
            # The actual level will be converted to integer internally
            assert logger.level != 0, "Logger level should be set"

    def test_formatter_application(self):
        """Test that formatter is properly applied to handlers."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            with patch("fivcadvisor.logs.settings.default_logger_config", {}):
                custom_format = "CUSTOM: %(levelname)s - %(message)s"
                logger = create_default_logger(
                    name="test_formatter", file=log_file, format=custom_format
                )

                # Check that handler has formatter
                handler = logger.handlers[0]
                assert handler.formatter is not None, "Handler should have formatter"

                # Check that the formatter has the correct format string
                # This is the most reliable way to test formatter application
                formatter_format = handler.formatter._fmt
                assert (
                    formatter_format == custom_format
                ), f"Formatter should use custom format, got: {formatter_format}"

        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_rotating_file_handler_configuration(self):
        """Test that RotatingFileHandler is configured correctly."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            log_file = f.name

        try:
            with patch("fivcadvisor.logs.settings.default_logger_config", {}):
                logger = create_default_logger(
                    name="test_rotating_config", file=log_file
                )

                handler = logger.handlers[0]
                assert isinstance(
                    handler, RotatingFileHandler
                ), "Should be RotatingFileHandler"
                assert handler.maxBytes == 1048576, "Should have 1MB max size"
                assert handler.backupCount == 7, "Should keep 7 backup files"
                # RotatingFileHandler uses 'a' mode, not 'a+'
                assert handler.mode == "a", "Should be in append mode"

        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

"""
Session management for FivcAdvisor flows.

This module provides a file-based session manager for tracking
flow execution and events.
"""

import os
import time
from uuid import uuid4


class FileSessionManager(object):
    """Manager for handling multiple sessions."""

    def __init__(self, path):
        assert os.path.isdir(path)
        self.path = path

    def create_session(self):
        """Create a new session."""
        session_id = str(uuid4())
        session_path = os.path.join(self.path, session_id)
        if os.path.exists(session_path):
            return session_id
            # raise FileExistsError(
            #     f'Session already exists: {session_path}')

        return FileSession(session_id, session_path)

    def get_session(self, session_id):
        session_path = os.path.join(self.path, session_id)
        if not os.path.isfile(session_path):
            return None
            # raise FileNotFoundError(
            #     f'Session not found: {session_path}')

        return FileSession(session_id, session_path)


class FileSession(object):
    """Session for managing flow execution."""

    def __init__(self, session_id, path):
        self.id = session_id
        self.path = path
        self.get_cursor = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # remove session file
        if os.path.exists(self.path):
            os.remove(self.path)

    def put(self, event: str):
        """Put an event into the session."""
        # append to file
        with open(self.path, "a") as f:
            if not event.endswith("\n\n"):
                event += "\n\n"
            f.write(event)

    def get(self, timeout: float = 2.0):
        """
        Get new messages from the session file.

        Monitors the file for changes and returns new messages that haven't been read yet.
        Messages are separated by double newlines ('\n\n').

        Args:
            timeout: Maximum time to wait for new messages in seconds

        Returns:
            str: The next unread message, or None if timeout occurs

        Raises:
            FileNotFoundError: If the session file has been deleted
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if file still exists
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Session file has been deleted: {self.path}")

            try:
                # Read file content from current cursor position
                with open(self.path, "r", encoding="utf-8") as f:
                    f.seek(self.get_cursor)
                    new_content = f.read()

                    if new_content:
                        # Split by double newlines to get messages
                        messages = new_content.split("\n\n")

                        # If we have at least one complete message (ending with \n\n)
                        if len(messages) > 1:
                            # The first message is complete
                            message = messages[0]

                            # Update cursor to skip this message and its separator
                            message_length = len(message) + 2  # +2 for '\n\n'
                            self.get_cursor += message_length

                            return message

                        # If we only have partial content (no complete message yet)
                        # Don't update cursor, wait for more content

            except (IOError, OSError):
                # File might be temporarily unavailable, continue waiting
                pass

            # Wait a bit before checking again
            time.sleep(0.1)

        # Timeout reached, return None
        return None

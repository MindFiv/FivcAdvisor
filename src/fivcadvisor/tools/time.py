"""Time tool for CrewAI - provides current local date/time in various formats."""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from fivcadvisor.tools import decorators


class TimeInput(BaseModel):
    fmt: Optional[str] = Field(
        description="Custom format string for datetime output. "
        "Uses Python's strftime format codes. If null (default), "
        "returns ISO 8601 format.",
        default=None,
    )


@decorators.tool("Local Time", args_schema=TimeInput)
def local_time(fmt: Optional[str] = None) -> str:
    """
    Get the current local date and time in a specified format.

    This function retrieves the current local date and time from the system
    and returns it as a formatted string. By default, it returns ISO 8601 format,
    but can accept custom format strings for flexible output formatting.
    The time is based on the system's local timezone.

    Args:
        fmt (Optional[str], optional): Custom format string for datetime output.
            Uses Python's strftime format codes. If null (default), returns
            ISO 8601 format. Defaults to null.

    Returns:
        str: Current local date and time in the specified format.
             - If fmt is null: ISO 8601 format "YYYY-MM-DDTHH:MM:SS[.ffffff]"
             - If fmt is provided: Custom formatted string according to fmt

    Examples:
        >>> local_time()
        '2025-01-15T14:30:45'

        >>> local_time(fmt="%Y-%m-%d %H:%M:%S")
        '2025-01-15 14:30:45'

        >>> local_time(fmt="%B %d, %Y at %I:%M %p")
        'January 15, 2025 at 02:30 PM'

        >>> local_time(fmt="%A, %b %d")
        'Wednesday, Jan 15'

        >>> local_time(fmt="%Y%m%d_%H%M%S")
        '20250115_143045'

    Common Format Codes:
        %Y - 4-digit year (2025)
        %m - Month as number (01-12)
        %d - Day of month (01-31)
        %H - Hour 24-hour format (00-23)
        %I - Hour 12-hour format (01-12)
        %M - Minute (00-59)
        %S - Second (00-59)
        %p - AM/PM
        %A - Full weekday name
        %B - Full month name
        %b - Abbreviated month name

    Note:
        - The returned time is always in the system's local timezone
        - No timezone offset information is included in the output
        - Invalid format strings will raise a ValueError
        - For complete format code reference, see Python's strftime documentation

    Raises:
        Returns error message as string if any exception occurs during execution.
        Possible error scenarios:
        - ValueError: If fmt contains invalid format codes or datetime formatting fails
        - Exception: Any other unexpected system errors

    See Also:
        datetime.datetime.now(): The underlying method used to get current time
        datetime.datetime.strftime(): The method used for custom formatting
        datetime.datetime.isoformat(): The method used for default ISO formatting
    """
    try:
        # Get current local time
        now = datetime.now()
        return now.strftime(fmt) if fmt else now.isoformat()

    except ValueError as e:
        # Return user-friendly error messages
        return f"Error: {e}"
    except Exception as e:
        # Catch any unexpected errors
        return f"Unexpected error: {type(e).__name__}: {e}"


__all__ = ["local_time"]

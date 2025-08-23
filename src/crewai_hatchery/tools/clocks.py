from __future__ import annotations

import json
from datetime import datetime
from urllib import request as _urlreq

from crewai.tools import tool  # type: ignore


@tool("Local Clock")
def local_clock(detail: object = "human") -> str:
    """
    Get the current local date & time.

    Args:
        detail: Output style. One of:
          - "human" -> e.g. "Fri, 23 Aug 2025, 14:05:30 PDT"
          - "iso"   -> ISO 8601 with timezone offset
          - "unix"  -> Seconds since Unix epoch
          - Any other value is treated as a strftime format string

    Note:
        CrewAI may pass arguments as a dict. This function accepts both a string
        (the desired detail) or a dict with a "detail" key.
    """
    try:
        # Normalize input coming from different tool invocation styles
        if isinstance(detail, dict):  # e.g., {"detail": "human"}
            detail_value = detail.get("detail", "human")
        elif detail is None or detail == "":
            detail_value = "human"
        else:
            detail_value = str(detail)

        now = datetime.now().astimezone()
        dl = detail_value.lower()
        if dl == "human":
            return now.strftime("%a, %d %b %Y, %H:%M:%S %Z")
        if dl == "iso":
            return now.isoformat()
        if dl == "unix":
            return str(int(now.timestamp()))
        # Treat as custom strftime pattern
        return now.strftime(detail_value)
    except Exception as e:
        # Return error string so the agent can react or try a different format
        return f"Error: {e}"


@tool("Online Clock")
def online_clock(detail: object = "human") -> str:
    """
    Get the current time from the internet (via worldtimeapi.org).

    Args:
        detail: Output style. One of:
          - "human" -> e.g. "Fri, 23 Aug 2025, 14:05:30 UTC"
          - "iso"   -> ISO 8601 with timezone offset (from API)
          - "unix"  -> Seconds since Unix epoch (from API)
          - Any other value is treated as a strftime format string

    Notes:
        - Accepts either a string (detail) or a dict, e.g., {"detail": "iso", "timezone": "Etc/UTC"}
        - Defaults to timezone "Etc/UTC" for determinism.
    """
    try:
        # Normalize input and extract optional timezone if provided
        timezone = "Etc/UTC"
        if isinstance(detail, dict):
            timezone = str(detail.get("timezone") or timezone)
            detail_value = str(detail.get("detail", "human"))
        elif detail is None or detail == "":
            detail_value = "human"
        else:
            detail_value = str(detail)

        url = f"https://worldtimeapi.org/api/timezone/{timezone}"
        with _urlreq.urlopen(url, timeout=8) as resp:  # nosec - public API
            data = json.loads(resp.read().decode("utf-8"))

        iso = data.get("datetime") or data.get("utc_datetime")
        unix = data.get("unixtime")
        if iso is None and unix is not None:
            # Fallback: build ISO from unix in UTC
            from datetime import timezone as _tz

            iso = datetime.fromtimestamp(int(unix), tz=_tz.utc).isoformat()
        if iso is None:
            raise ValueError("No datetime in response")

        dl = detail_value.lower()
        if dl == "iso":
            return str(iso)
        if dl == "unix":
            return str(unix)

        # For human/custom, format using Python's datetime
        # Parse ISO (Python 3.11+ handles offset); 3.9 supports fromisoformat too
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if dl == "human":
            return dt.strftime("%a, %d %b %Y, %H:%M:%S %Z")
        return dt.strftime(detail_value)
    except Exception as e:
        return f"Error: {e}"


__all__ = ["local_clock", "online_clock"]

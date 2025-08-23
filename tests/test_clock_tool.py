import json
from contextlib import contextmanager

from crewai_hatchery.tools import create_tools_retriever
from crewai_hatchery.tools.clocks import local_clock, online_clock


@contextmanager
def mock_urlopen(payload: dict):
    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    from urllib import request as _urlreq

    orig = _urlreq.urlopen
    _urlreq.urlopen = lambda *a, **k: _Resp()
    try:
        yield
    finally:
        _urlreq.urlopen = orig


def _run_clock(tool, detail=None) -> str:
    try:
        return tool.run({"detail": detail}) if detail is not None else tool.run()
    except Exception:
        # Some tools accept positional string arg
        return tool.run(detail) if detail is not None else tool.run("")


def test_local_clock_direct_human():
    out = _run_clock(local_clock, "human")
    assert "," in out and out.count(":") >= 2  # coarse structure check


def test_online_clock_iso():
    with mock_urlopen(
        {"datetime": "2025-08-23T14:05:30+00:00", "unixtime": 1755967530}
    ):
        out = _run_clock(online_clock, "iso")
    assert out == "2025-08-23T14:05:30+00:00"


def test_online_clock_unix():
    with mock_urlopen(
        {"datetime": "2025-08-23T14:05:30+00:00", "unixtime": 1755967530}
    ):
        out = _run_clock(online_clock, "unix")
    assert out == "1755967530"


def test_online_clock_human():
    with mock_urlopen(
        {"datetime": "2025-08-23T14:05:30+00:00", "unixtime": 1755967530}
    ):
        out = _run_clock(online_clock, "human")
    assert "," in out and out.count(":") >= 2


def test_online_clock_custom_format():
    with mock_urlopen(
        {"datetime": "2025-08-23T14:05:30+00:00", "unixtime": 1755967530}
    ):
        out = _run_clock(online_clock, "%Y-%m-%d %H:%M")
    assert out == "2025-08-23 14:05"

    out = _run_clock(local_clock, "human")
    assert "," in out and out.count(":") >= 2  # coarse structure check


def test_local_clock_direct_iso():
    out = _run_clock(local_clock, "iso")
    assert "T" in out and ("+" in out or "Z" in out or "-" in out)


def test_local_clock_direct_unix():
    out = _run_clock(local_clock, "unix")
    assert out.isdigit() and len(out) >= 10


def test_local_clock_custom_format():
    out = _run_clock(local_clock, "%Y-%m-%d %H:%M")
    # Expect pattern like 2025-08-23 14:05
    assert len(out) >= 16 and out[4] == "-" and out[7] == "-" and out[10] == " "


def test_retriever_includes_clock():
    retriever = create_tools_retriever()
    tool = retriever.get("Local Clock")
    assert tool is not None
    out = _run_clock(tool, "human")
    assert isinstance(out, str) and len(out) > 0

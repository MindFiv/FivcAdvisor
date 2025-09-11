from fivcadvisor.tools import create_retriever, create_default_tools
from fivcadvisor.tools.calculators import basic_calculator


def _run_calc(tool, expr: str) -> str:
    # Try both common invocation styles for CrewAI tools
    try:
        return tool.run(expr)
    except Exception:
        return tool.run({"expression": expr})


def test_basic_calculator_direct():
    assert _run_calc(basic_calculator, "2 + 2") == "4"
    assert _run_calc(basic_calculator, "2 * (3 + 4)") == "14"
    assert _run_calc(basic_calculator, "(1 + 2) ** 3 / 9") == "3"


def test_basic_calculator_errors():
    assert _run_calc(basic_calculator, "").startswith("Error:")
    assert _run_calc(basic_calculator, "sin(1)").startswith("Error:")
    assert _run_calc(basic_calculator, "a + 1").startswith("Error:")


def test_retriever_includes_calculator():
    retriever = create_retriever()
    create_default_tools(tools_retriever=retriever)
    tool = retriever.get("Calculator")
    assert tool is not None
    # ensure it executes
    result = _run_calc(tool, "10 // 3")
    assert result == "3"

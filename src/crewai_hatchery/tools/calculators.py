from __future__ import annotations

import ast
import operator as _op
from typing import Union, Callable

from crewai.tools import tool  # type: ignore

Number = Union[int, float]

# Allowed operators for safe evaluation
_ALLOWED_BINOPS: dict[type[ast.AST], Callable] = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.FloorDiv: _op.floordiv,
    ast.Mod: _op.mod,
    ast.Pow: _op.pow,
}

_ALLOWED_UNARY: dict[type[ast.AST], Callable] = {
    ast.UAdd: _op.pos,
    ast.USub: _op.neg,
}


def _eval_node(node: ast.AST) -> Number:
    """Recursively and safely evaluate a limited math AST."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric literals are allowed")

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:  # noqa: E721
        return _ALLOWED_UNARY[type(node.op)](_eval_node(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:  # noqa: E721
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_BINOPS[type(node.op)](left, right)

    if isinstance(
        node, ast.Paren
    ):  # not actually produced by ast.parse; kept for clarity
        return _eval_node(node.value)  # type: ignore[attr-defined]

    raise ValueError(
        "Unsupported expression. Allowed: numbers, +, -, *, /, //, %, ** and parentheses"
    )


def _safe_eval(expr: str) -> Number:
    expr = expr.strip()
    if not expr:
        raise ValueError("Empty expression")

    # Fast sanity check: disallow any forbidden characters that could lead to names/calls
    forbidden_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_`$@[]{}:=;\\\n\t\r"
    )
    if any(c in forbidden_chars for c in expr):
        # Still parse to provide a consistent error message if it's just spaces/parentheses
        raise ValueError(
            "Only numeric expressions are allowed (no variables or function calls)"
        )

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid expression: {e.msg}") from e

    result = _eval_node(tree)

    # Normalize -0.0 to 0
    if isinstance(result, float) and result == 0:
        result = 0.0

    return result


@tool("Basic Calculator")
def basic_calculator(expression: str) -> str:
    """
    Evaluate a basic math expression safely.

    Supported: +, -, *, /, //, %, **, parentheses. No variables or functions.
    Examples:
      - 2 + 2
      - 2 * (3 + 4)
      - (1 + 2) ** 3 / 7
    """
    try:
        value = _safe_eval(expression)
        # Present integers without trailing .0
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return str(value)
    except Exception as e:  # return error string so agent can react
        return f"Error: {e}"


__all__ = ["basic_calculator"]

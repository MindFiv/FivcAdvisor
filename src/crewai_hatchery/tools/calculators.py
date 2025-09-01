"""Calculator tool for CrewAI - provides safe mathematical expression evaluation."""

import re
from typing import Union

from pydantic import BaseModel, Field

from crewai_hatchery.tools import decorators


# Type alias for numeric values
Number = Union[int, float]


class CalculatorInput(BaseModel):
    expression: str = Field(
        description="Mathematical expression to evaluate. "
        "Supports +, -, *, /, //, %, ^ (power), ** (power), and parentheses. "
        "Only numeric expressions allowed - no variables or functions.",
    )


@decorators.tool("Calculator", args_schema=CalculatorInput)
def basic_calculator(expression: str) -> str:
    """
    Calculate mathematical expressions - use this tool whenever you need to perform math calculations.

    This is a comprehensive calculator that can solve mathematical problems, compute numerical values,
    and evaluate arithmetic expressions. Use this tool for any mathematical computation needs including
    basic arithmetic, complex expressions with parentheses, and calculations involving decimals.

    **When to use this tool:**
    - Need to calculate numbers, solve math problems, or compute values
    - Perform arithmetic operations like addition, subtraction, multiplication, division
    - Calculate percentages, powers, or modulo operations
    - Evaluate complex mathematical expressions with multiple operations
    - Work with decimal numbers and negative numbers
    - Need precise numerical results for any mathematical computation

    **Supported mathematical operations:**
    - Addition (+): Add numbers together
    - Subtraction (-): Subtract one number from another
    - Multiplication (*): Multiply numbers
    - Division (/): Divide numbers
    - Floor Division (//): Integer division (rounds down)
    - Modulo (%): Get remainder after division
    - Exponentiation (^ or **): Raise to a power
    - Parentheses (): Group operations and control order of calculation

    Args:
        expression (str): Mathematical expression to calculate. Can include numbers, operators (+, -, *, /, %, ^),
                         and parentheses. Examples: "2+2", "10*5-3", "(15+5)/4", "2^3*4"

    Returns:
        str: The calculated numerical result. Whole numbers returned as integers,
             decimals shown with appropriate precision.

    **Usage Examples:**
        Simple calculations:
        >>> basic_calculator("2 + 2")
        "4"
        >>> basic_calculator("100 - 25")
        "75"
        >>> basic_calculator("12 * 8")
        "96"
        >>> basic_calculator("144 / 12")
        "12"

        Advanced calculations:
        >>> basic_calculator("2^10")  # 2 to the power of 10
        "1024"
        >>> basic_calculator("2**10")  # Alternative power syntax
        "1024"
        >>> basic_calculator("10 // 3")  # Floor division
        "3"
        >>> basic_calculator("(20 + 30) * 2")  # Parentheses first
        "100"
        >>> basic_calculator("3.14159 * 2")  # Decimal numbers
        "6.28318"
        >>> basic_calculator("17 % 5")  # Remainder/modulo
        "2"

        Complex expressions:
        >>> basic_calculator("(5 + 3) * 2^3 - 10")
        "54"
        >>> basic_calculator("100 / (2 + 3) + 15")
        "35"

    **Error handling:**
    Returns clear error messages for invalid inputs like division by zero,
    mismatched parentheses, or invalid characters.

    **Note:** Only accepts numerical expressions - no variables, functions, or text.
    Follows standard mathematical order of operations (PEMDAS/BODMAS).
    """

    def _tokenize_expression(expression: str) -> list[str]:
        """Tokenize a mathematical expression into numbers and operators."""
        # Remove all whitespace
        expression = expression.replace(" ", "")

        # Check for invalid characters (now including * for ** operator)
        valid_chars = "0123456789+-*/().%^"
        if not all(c in valid_chars for c in expression):
            invalid_chars = set(c for c in expression if c not in valid_chars)
            raise ValueError(f"Invalid characters in expression: {invalid_chars}")

        # First, replace ** with ^ and // with a special token
        expression = expression.replace("**", "^")
        expression = expression.replace(
            "//", "§"
        )  # Use § as temporary token for floor division

        # Tokenize using regex (now including § for floor division)
        pattern = r"(\d+\.?\d*|[+\-*/()%^§])"
        tokens = re.findall(pattern, expression)

        # Verify we captured the entire expression
        if "".join(tokens) != expression:
            raise ValueError("Failed to parse expression completely")

        return tokens

    def _safe_power(base: Number, exponent: Number) -> Number:
        """Safely compute base^exponent with overflow protection."""
        # Prevent extremely large exponents that could hang the system
        if abs(exponent) > 1000:
            raise ValueError("Exponent too large (maximum 1000)")

        # Check for potential overflow situations
        if abs(base) > 1 and exponent > 100:
            # Rough check to prevent overflow
            if abs(base) ** 10 > 1e30:
                raise ValueError("Result would be too large")

        try:
            result = base**exponent
            # Check for infinity or NaN
            if not (-1e308 < result < 1e308):
                raise ValueError("Result is too large")
            return result
        except OverflowError:
            raise ValueError("Result is too large")

    def _evaluate_expression(tokens: list[str]) -> Number:
        """Evaluate a tokenized mathematical expression using order of operations."""

        def parse_number(token: str) -> Number:
            """Parse a token into a number."""
            try:
                if "." in token:
                    return float(token)
                return int(token)
            except ValueError:
                raise ValueError(f"Invalid number: {token}")

        def evaluate_flat(tokens: list[str]) -> Number:
            """Evaluate a flat expression (no parentheses) following order of operations."""
            if not tokens:
                raise ValueError("Empty expression")

            # Handle unary minus at the beginning
            if tokens[0] == "-" and len(tokens) > 1:
                tokens = ["0", "-"] + tokens[1:]

            # First pass: handle exponentiation (right to left)
            i = len(tokens) - 1
            while i >= 0:
                if i > 0 and i < len(tokens) - 1 and tokens[i] == "^":
                    left = parse_number(tokens[i - 1])
                    right = parse_number(tokens[i + 1])
                    result = _safe_power(left, right)
                    tokens = tokens[: i - 1] + [str(result)] + tokens[i + 2 :]
                else:
                    i -= 1

            # Second pass: handle multiplication, division, floor division, and modulo (left to right)
            i = 0
            while i < len(tokens):
                if i > 0 and i < len(tokens) - 1 and tokens[i] in ["*", "/", "§", "%"]:
                    left = parse_number(tokens[i - 1])
                    right = parse_number(tokens[i + 1])

                    if tokens[i] == "*":
                        result = left * right
                    elif tokens[i] == "/":
                        if right == 0:
                            raise ValueError("Division by zero")
                        result = left / right
                    elif tokens[i] == "§":  # Floor division
                        if right == 0:
                            raise ValueError("Division by zero")
                        result = left // right
                    else:  # %
                        if right == 0:
                            raise ValueError("Modulo by zero")
                        result = left % right

                    tokens = tokens[: i - 1] + [str(result)] + tokens[i + 2 :]
                    i -= 1
                else:
                    i += 1

            # Third pass: handle addition and subtraction (left to right)
            i = 0
            while i < len(tokens):
                if i > 0 and i < len(tokens) - 1 and tokens[i] in ["+", "-"]:
                    left = parse_number(tokens[i - 1])
                    right = parse_number(tokens[i + 1])

                    if tokens[i] == "+":
                        result = left + right
                    else:  # -
                        result = left - right

                    tokens = tokens[: i - 1] + [str(result)] + tokens[i + 2 :]
                    i -= 1
                else:
                    i += 1

            # Should have exactly one token left
            if len(tokens) != 1:
                raise ValueError("Invalid expression structure")

            return parse_number(tokens[0])

        def evaluate_with_parentheses(tokens: list[str]) -> Number:
            """Recursively evaluate expressions with parentheses."""
            # Find innermost parentheses
            depth = 0
            start = -1

            for i, token in enumerate(tokens):
                if token == "(":
                    if depth == 0:
                        start = i
                    depth += 1
                elif token == ")":
                    depth -= 1
                    if depth == 0 and start != -1:
                        # Evaluate the expression inside parentheses
                        inner = tokens[start + 1 : i]
                        if not inner:
                            raise ValueError("Empty parentheses")
                        result = evaluate_with_parentheses(inner)
                        tokens = tokens[:start] + [str(result)] + tokens[i + 1 :]
                        return evaluate_with_parentheses(tokens)

            if depth != 0:
                raise ValueError("Mismatched parentheses")

            # No more parentheses, evaluate the flat expression
            return evaluate_flat(tokens)

        return evaluate_with_parentheses(tokens)

    try:
        # Validate and clean the expression
        expression = expression.strip()
        if not expression:
            return "Error: Empty expression"

        # Tokenize the expression
        tokens = _tokenize_expression(expression)

        # Evaluate the expression
        result = _evaluate_expression(tokens)

        # Format the result
        # If it's a float that's actually a whole number, return it as an integer
        if isinstance(result, float) and result.is_integer() and abs(result) < 1e15:
            return str(int(result))

        # For very large or very small numbers, use scientific notation
        if isinstance(result, float) and (
            abs(result) > 1e10 or (abs(result) < 1e-5 and result != 0)
        ):
            return f"{result:.6e}"

        # For regular floats, limit decimal places for cleaner output
        if isinstance(result, float):
            # Remove trailing zeros after decimal point
            formatted = f"{result:.10f}".rstrip("0").rstrip(".")
            return formatted

        return str(result)

    except ValueError as e:
        # Return user-friendly error messages
        return f"Error: {e}"
    except Exception as e:
        # Catch any unexpected errors
        return f"Unexpected error: {type(e).__name__}: {e}"


__all__ = ["basic_calculator"]

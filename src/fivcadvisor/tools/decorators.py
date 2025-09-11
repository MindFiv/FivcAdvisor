from typing import Callable

from pydantic import BaseModel as PydanticBaseModel
from crewai.tools.base_tool import Tool, BaseTool


def tool(
    *args,
    args_schema: type[PydanticBaseModel] | None = None,
    result_as_answer: bool = False,
    max_usage_count: int | None = None,
) -> Callable:
    """
    Decorator to create a tool from a function.

    Args:
        *args: Positional arguments, either the function to decorate or the tool name.
        args_schema: Pydantic model for the tool arguments. If not provided, one will be created from the function annotations.
        result_as_answer: Flag to indicate if the tool result should be used as the final agent answer.
        max_usage_count: Maximum number of times this tool can be used. None means unlimited usage.
    """

    def _make_with_name(tool_name: str) -> Callable:
        def _make_tool(f: Callable) -> BaseTool:
            if f.__doc__ is None:
                raise ValueError("Function must have a docstring")
            if f.__annotations__ is None:
                raise ValueError("Function must have type annotations")

            class_name = "".join(tool_name.split()).title()
            schema = args_schema or type(
                class_name,
                (PydanticBaseModel,),
                {
                    "__annotations__": {
                        k: v for k, v in f.__annotations__.items() if k != "return"
                    },
                },
            )

            return Tool(
                name=tool_name,
                description=f.__doc__,
                func=f,
                args_schema=schema,
                result_as_answer=result_as_answer,
                max_usage_count=max_usage_count,
                current_usage_count=0,
            )

        return _make_tool

    if len(args) == 1 and callable(args[0]):
        return _make_with_name(args[0].__name__)(args[0])
    if len(args) == 1 and isinstance(args[0], str):
        return _make_with_name(args[0])
    raise ValueError("Invalid arguments")

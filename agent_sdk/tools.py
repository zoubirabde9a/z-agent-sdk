from typing import Any, Callable, Dict

from .schema import build_parameters_schema


def function_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to mark a function as an LLM-callable tool.
    
    This decorator adds metadata to the function that allows it to be
    exposed to the LLM as a tool with proper schema information.
    
    Args:
        func: The function to be marked as a tool
        
    Returns:
        The original function with added tool metadata
    """
    description = (func.__doc__ or "").strip() or f"Tool function {func.__name__}"
    parameters_schema, _ = build_parameters_schema(func)
    func._tool_spec = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": parameters_schema,
        },
    }
    return func

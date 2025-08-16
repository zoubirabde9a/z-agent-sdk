import inspect
from typing import Any, Callable, Dict, List, Tuple


def python_type_to_json_schema(py_type: Any) -> Dict[str, Any]:
    """Convert Python type annotations to JSON schema.
    
    Args:
        py_type: Python type annotation
        
    Returns:
        Equivalent JSON schema representation
    """
    # Minimal typing -> JSON schema mapper
    origin = getattr(py_type, "__origin__", None)
    args = getattr(py_type, "__args__", ())
    if origin is list or origin is List:
        item_type = args[0] if args else Any
        return {"type": "array", "items": python_type_to_json_schema(item_type)}
    if origin is dict or origin is Dict:
        return {"type": "object"}
    if py_type in (str,):
        return {"type": "string"}
    if py_type in (int,):
        return {"type": "integer"}
    if py_type in (float,):
        return {"type": "number"}
    if py_type in (bool,):
        return {"type": "boolean"}
    return {"type": "string"}


def build_parameters_schema(func: Callable[..., Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Build JSON schema for function parameters.
    
    Args:
        func: Function to analyze
        
    Returns:
        Tuple containing (parameter schema, required parameters list)
    """
    sig = inspect.signature(func)
    properties: Dict[str, Any] = {}
    required: List[str] = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        annotation = param.annotation if param.annotation is not inspect._empty else str
        schema = python_type_to_json_schema(annotation)
        if param.default is not inspect._empty:
            schema["default"] = param.default
        else:
            required.append(name)
        properties[name] = schema

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }, required

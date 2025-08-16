import inspect
import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from openai import OpenAI
except ImportError as exc:
    raise SystemExit(
        "The 'openai' package is required. Install with: pip install -r requirements.txt"
    ) from exc


def _python_type_to_json_schema(py_type: Any) -> Dict[str, Any]:
    # Minimal typing -> JSON schema mapper
    origin = getattr(py_type, "__origin__", None)
    args = getattr(py_type, "__args__", ())
    if origin is list or origin is List:
        item_type = args[0] if args else Any
        return {"type": "array", "items": _python_type_to_json_schema(item_type)}
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


def _build_parameters_schema(func: Callable[..., Any]) -> Tuple[Dict[str, Any], List[str]]:
    sig = inspect.signature(func)
    properties: Dict[str, Any] = {}
    required: List[str] = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        annotation = param.annotation if param.annotation is not inspect._empty else str
        schema = _python_type_to_json_schema(annotation)
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


def function_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    description = (func.__doc__ or "").strip() or f"Tool function {func.__name__}"
    parameters_schema, _ = _build_parameters_schema(func)
    func._tool_spec = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": parameters_schema,
        },
    }
    return func


@dataclass
class Agent:
    name: str
    instructions: str
    tools: List[Callable[..., Any]] = field(default_factory=list)
    handoff_description: Optional[str] = None

    def tool_specs(self) -> List[Dict[str, Any]]:
        specs: List[Dict[str, Any]] = []
        for t in self.tools:
            spec = getattr(t, "_tool_spec", None)
            if spec:
                specs.append(spec)
        return specs

    def tool_map(self) -> Dict[str, Callable[..., Any]]:
        mapping: Dict[str, Callable[..., Any]] = {}
        for t in self.tools:
            mapping[t.__name__] = t
        return mapping


class Runner:
    @staticmethod
    def run(agent: Agent, user_input: str, model: str = "gpt-4o-mini") -> str:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")

        client = OpenAI()

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": agent.instructions},
            {"role": "user", "content": user_input},
        ]

        tools = agent.tool_specs()
        tool_name_to_func = agent.tool_map()

        # First call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
        )

        message = response.choices[0].message

        if not getattr(message, "tool_calls", None):
            return message.content or ""

        # Execute tool calls and send results back for final answer
        tool_outputs: List[Dict[str, Any]] = []
        for tool_call in message.tool_calls:
            if not tool_call.function:
                continue
            func_name = tool_call.function.name
            func = tool_name_to_func.get(func_name)
            if not func:
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps({"error": f"Unknown tool: {func_name}"}),
                })
                continue
            try:
                args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            try:
                result = func(**args)
                # Ensure JSON-serializable content
                serialized = json.dumps(result, ensure_ascii=False, default=str)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": serialized,
                })
            except Exception as exc:
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps({"error": str(exc)}),
                })

        final = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": agent.instructions},
                {"role": "user", "content": user_input},
                message,
                *[
                    {"role": "tool", "tool_call_id": out["tool_call_id"], "content": out["output"]}
                    for out in tool_outputs
                ],
            ],
        )
        return final.choices[0].message.content or ""



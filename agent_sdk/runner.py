import json
from typing import Any, Dict, List

try:
    from openai import OpenAI
except ImportError as exc:
    raise SystemExit(
        "The 'openai' package is required. Install with: pip install -r requirements.txt"
    ) from exc

from .agent import Agent
from .llm_provider import LLMProvider


class Runner:
    """Executes agents with the OpenAI API.
    
    This class handles the execution flow for agents, including:
    - Setting up the OpenAI client
    - Managing the conversation
    - Handling tool calls and responses
    """
    
    @staticmethod
    def run(agent: Agent, user_input: str, model: str = "gpt-4o-mini") -> str:
        """Run an agent with the given user input.
        
        Args:
            agent: The agent to run
            user_input: The user's input message
            model: The OpenAI model to use (default: gpt-4o-mini)
            
        Returns:
            The agent's final response
            
        Raises:
            RuntimeError: If API key is not set
        """
        # Resolve API key and base URL from static provider or environment
        api_key = LLMProvider.API_KEY
        base_url = LLMProvider.BASE_URL

        if not api_key:
            raise RuntimeError("api key is not set. Provide via set_llm_provider() or environment.")

        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

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

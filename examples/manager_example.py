import os
import sys
import pathlib
from dotenv import load_dotenv
from typing import Any

# Allow running this example directly: python examples/manager_example.py
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sdk.agent_sdk import Agent, Runner, function_tool, set_llm_provider


@function_tool
def create_ticket(issue: str) -> str:
    """
    Create a ticket in the system for an issue to be resolved.
    """
    print(f"Creating ticket for issue: {issue}")
    return "Ticket created. ID: 12345"


manager_agent = Agent(
    name="Manager",
    handoff_description="Handles escalated issues that require managerial attention",
    instructions=(
        "You handle escalated customer issues that the initial custom service agent could not resolve. "
        "You will receive the issue and the reason for escalation. If the issue cannot be immediately resolved for the "
        "customer, create a ticket in the system and inform the customer."
    ),
    tools=[create_ticket],
)


def main() -> None:
    load_dotenv()
    
    if not os.getenv("API_KEY"):
        print("Warning: API_KEY is not set. The SDK call will fail without it.")

    if not os.getenv("BASE_URL"):
        print("Warning: BASE_URL is not set. The SDK call will fail without it.")

    if not os.getenv("MODEL"):
        print("Warning: MODEL is not set. Falling back to default model.")

    api_key = os.getenv("API_KEY") or ""
    base_url = os.getenv("BASE_URL") or None
    model = os.getenv("MODEL") or "gpt-4o-mini"

    set_llm_provider(api_key, base_url)

    print("Manager agent ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        reply = Runner.run(manager_agent, user_input, model=model)
        print(f"Manager: {reply}\n")


if __name__ == "__main__":
    main()



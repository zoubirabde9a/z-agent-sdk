from typing import Optional


class LLMProvider:
    """Static configuration for the LLM provider.

    Values set here are used by the runner unless overridden by environment variables.
    """
    API_KEY: Optional[str] = None
    BASE_URL: Optional[str] = None


def set_llm_provider(api_key: str, base_url: Optional[str] = None) -> None:
    """Set static credentials and endpoint for the LLM provider used by the runner.

    - api_key: Provider API key
    - base_url: Optional custom base URL for the provider (e.g., self-hosted endpoint)
    """
    LLMProvider.API_KEY = api_key
    LLMProvider.BASE_URL = base_url

"""OpenAI client factory for OpenAI Platform."""

import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


def get_openai_client() -> OpenAI:
    """Create and return configured OpenAI client."""
    if OpenAI is None:
        raise ImportError(
            "openai package is not installed. Install it with: uv add openai"
        )
    
    settings = get_settings()
    
    # Validate API key is present and not empty
    api_key = settings.openai_api_key
    if not api_key or not api_key.strip():
        raise ValueError(
            "OPENAI_API_KEY is not set or is empty in .env file. "
            "Please add your OpenAI API key to the .env file.\n"
            "Example: OPENAI_API_KEY=sk-..."
        )
    
    api_key_clean = api_key.strip()
    if not api_key_clean.startswith(("sk-", "sk_proj-", "sess-")):
        logger.warning(
            f"API key format might be invalid for OpenAI Platform. "
            f"OpenAI API keys typically start with 'sk-'. "
            f"Got: '{api_key_clean[:7]}...'"
        )
    
    client_kwargs = {"api_key": api_key_clean}
    if settings.openai_base_url:
        client_kwargs["base_url"] = settings.openai_base_url
    
    client = OpenAI(**client_kwargs)
    
    return client

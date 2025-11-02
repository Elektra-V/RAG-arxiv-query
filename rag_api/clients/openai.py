"""OpenAI client factory for OpenAI Platform."""

import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


def get_openai_client() -> OpenAI:
    """Create and return a configured OpenAI client for OpenAI Platform.
    
    Returns:
        Configured OpenAI client ready for use
        
    Raises:
        ImportError: If openai package is not installed
        ValueError: If API key is missing
    """
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
    
    # Validate API key format
    api_key_clean = api_key.strip()
    if not api_key_clean.startswith(("sk-", "sk_proj-", "sess-")):
        logger.warning(
            f"⚠️  API key format might be invalid. "
            f"OpenAI API keys typically start with 'sk-'. "
            f"Got: '{api_key_clean[:7]}...'"
        )
    
    client = OpenAI(api_key=api_key_clean)
    
    logger.info("✓ OpenAI Platform: Using API key authentication")
    
    return client

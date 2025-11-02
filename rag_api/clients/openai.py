"""OpenAI client factory for OpenAI Platform."""

import logging
from typing import Optional

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
    
    if not settings.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY must be set. Check your .env file."
        )
    
    client = OpenAI(api_key=settings.openai_api_key)
    
    logger.info("✓ OpenAI Platform: Using API key authentication")
    
    return client

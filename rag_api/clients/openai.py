"""OpenAI client factory for company API gateway with Basic authentication."""

from __future__ import annotations

import logging
from base64 import b64encode
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


def get_openai_client() -> OpenAI:
    """Create and return a configured OpenAI client for company API gateway.
    
    Automatically handles:
    - Basic authentication (username:password)
    - Custom base URL
    - Custom headers (if configured)
    
    Returns:
        Configured OpenAI client ready for use
        
    Raises:
        ImportError: If openai package is not installed
    """
    if OpenAI is None:
        raise ImportError(
            "openai package is not installed. Install it with: uv add openai"
        )
    
    settings = get_settings()
    
    # Get credentials from settings
    api_key = settings.openai_api_key or "xxxx"
    base_url = settings.openai_base_url
    username = settings.openai_auth_username
    password = settings.openai_auth_password
    
    # Build headers
    headers = {}
    
    # Add Basic auth if credentials provided
    if username and password:
        token = b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
        logger.debug(f"Configured Basic auth for {base_url}")
    
    # Add custom headers if configured
    if settings.company_api_extra_headers:
        try:
            for pair in settings.company_api_extra_headers.split(","):
                pair = pair.strip()
                if ":" in pair:
                    name, value = pair.split(":", 1)
                    headers[name.strip()] = value.strip()
                    logger.debug(f"Added custom header: {name.strip()}")
        except Exception as e:
            logger.warning(f"Failed to parse custom headers: {e}")
    
    # Create client
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers=headers if headers else None,
    )
    
    return client

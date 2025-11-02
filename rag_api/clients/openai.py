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
    
    Matches the exact pattern from company API documentation:
    - Uses Basic authentication (username:password)
    - Base64 encodes credentials
    - Sets Authorization header in default_headers
    - Uses custom base_url
    
    Returns:
        Configured OpenAI client ready for use
        
    Raises:
        ImportError: If openai package is not installed
        ValueError: If required credentials are missing
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
    
    # Validate required credentials
    if not username or not password:
        raise ValueError(
            "OPENAI_AUTH_USERNAME and OPENAI_AUTH_PASSWORD must be set "
            "for company API gateway. Check your .env file."
        )
    
    if not base_url:
        raise ValueError(
            "OPENAI_BASE_URL must be set. Check your .env file."
        )
    
    # Build Basic auth token (exact pattern from company API docs)
    token_string = f"{username}:{password}"
    token_bytes = b64encode(token_string.encode())
    auth_header = f"Basic {token_bytes.decode()}"
    
    # Build headers dictionary
    headers = {"Authorization": auth_header}
    
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
    
    # Log authentication setup (masked credentials)
    logger.info(
        f"Creating OpenAI client for {base_url} "
        f"(username: {username[:3]}..., auth: Basic)"
    )
    
    # Create client - matches company API reference exactly
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers=headers,
    )
    
    return client

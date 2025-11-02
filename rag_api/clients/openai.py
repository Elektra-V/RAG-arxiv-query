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
    
    base_url = settings.openai_base_url
    username = settings.openai_auth_username
    password = settings.openai_auth_password
    api_key = settings.openai_api_key
    
    # Detect authentication mode
    has_basic_auth = username and password
    has_api_key = bool(api_key)
    
    # Validate: Need at least one authentication method
    if not has_basic_auth and not has_api_key:
        raise ValueError(
            "Either OPENAI_AUTH_USERNAME/OPENAI_AUTH_PASSWORD (for gateway) "
            "OR OPENAI_API_KEY (for OpenAI Platform) must be set. Check your .env file."
        )
    
    if not base_url:
        raise ValueError(
            "OPENAI_BASE_URL must be set. Check your .env file."
        )
    
    # Build client kwargs
    client_kwargs = {"base_url": base_url}
    headers = {}
    
    # Gateway mode: Basic auth (preferred for free models)
    if has_basic_auth:
        token_string = f"{username}:{password}"
        token_bytes = b64encode(token_string.encode())
        headers["Authorization"] = f"Basic {token_bytes.decode()}"
        logger.info(
            f"Using Basic auth for gateway {base_url} "
            f"(username: {username[:3]}..., free models)"
        )
    
    # Platform mode: API key (for paid OpenAI Platform access)
    elif has_api_key:
        client_kwargs["api_key"] = api_key
        logger.info(f"Using API key authentication for OpenAI Platform {base_url}")
    
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
    
    # Set default_headers if we have any (Basic auth or custom headers)
    if headers:
        client_kwargs["default_headers"] = headers
    
    # Create client
    client = OpenAI(**client_kwargs)
    
    return client

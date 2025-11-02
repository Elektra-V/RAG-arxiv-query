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
    
    # When using Basic auth, don't pass api_key to avoid Bearer token conflict
    # SDK automatically adds Authorization: Bearer <api_key> if api_key is provided
    # This conflicts with our Basic auth header, causing 401 errors
    client_kwargs = {
        "base_url": base_url,
        "default_headers": headers,
    }
    
    # Only include api_key if provided AND no Basic auth (for OpenAI Platform direct access)
    # For gateway with Basic auth, api_key is not needed and causes conflicts
    if api_key and not (username and password):
        client_kwargs["api_key"] = api_key
        logger.info(f"Using API key authentication for {base_url}")
    else:
        logger.info(
            f"Using Basic auth for {base_url} "
            f"(username: {username[:3]}..., no API key needed for gateway)"
        )
    
    # Create client
    client = OpenAI(**client_kwargs)
    
    return client

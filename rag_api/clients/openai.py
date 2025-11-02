"""OpenAI client factory for company API gateway with Basic authentication.

Primary mode: Gateway with Basic auth (free models like Qwen with tooling support)
Fallback mode: OpenAI Platform with API key (paid, when Basic auth not available)
"""

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
    
    Primary mode (recommended): Gateway with Basic auth
    - Uses Basic authentication (username:password) for free models
    - Perfect for Qwen models with tooling support
    - No API key needed - completely free
    
    Fallback mode: OpenAI Platform with API key
    - Used only if Basic auth credentials not provided
    - Requires valid OpenAI Platform API key (paid)
    
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
    
    # Gateway mode (primary): Basic auth for free models with tooling support
    has_basic_auth = username and password
    
    # Platform mode (fallback): API key for paid OpenAI Platform access
    has_api_key = bool(api_key)
    
    # Validate base URL
    if not base_url:
        raise ValueError(
            "OPENAI_BASE_URL must be set. Check your .env file."
        )
    
    # Gateway mode is the primary and recommended path
    if has_basic_auth:
        if not username or not password:
            raise ValueError(
                "OPENAI_AUTH_USERNAME and OPENAI_AUTH_PASSWORD must be set "
                "for gateway mode (recommended for free Qwen models with tooling). "
                "Check your .env file."
            )
        
        # Build Basic auth header (matches company API documentation exactly)
        token_string = f"{username}:{password}"
        token_bytes = b64encode(token_string.encode())
        auth_header = f"Basic {token_bytes.decode()}"
        
        # SDK requires api_key parameter even with Basic auth (for validation)
        # We use placeholder "xxxx" - Basic auth header takes precedence
        client_kwargs = {
            "api_key": "xxxx",  # Placeholder - SDK requires this, but Basic auth header is used
            "base_url": base_url,
            "default_headers": {"Authorization": auth_header},
        }
        
        logger.info(
            f"✓ Gateway mode: Using Basic auth for {base_url} "
            f"(username: {username[:3]}..., free Qwen models with tooling support)"
        )
        
    # Platform mode (fallback only - when Basic auth not available)
    elif has_api_key:
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set for Platform mode. "
                "For gateway mode (recommended), use OPENAI_AUTH_USERNAME and OPENAI_AUTH_PASSWORD instead."
            )
        
        client_kwargs = {
            "base_url": base_url,
            "api_key": api_key,
        }
        
        logger.info(f"⚠ Platform mode: Using API key for {base_url} (paid)")
        
    else:
        raise ValueError(
            "Authentication required. Set OPENAI_AUTH_USERNAME and OPENAI_AUTH_PASSWORD "
            "for gateway mode (recommended - free Qwen models with tooling). "
            "Or set OPENAI_API_KEY for Platform mode (paid). Check your .env file."
        )
    
    # Build headers for custom headers (applies to both modes)
    headers = {}
    
    # Add custom headers if configured (for gateway mode)
    if settings.company_api_extra_headers and has_basic_auth:
        try:
            for pair in settings.company_api_extra_headers.split(","):
                pair = pair.strip()
                if ":" in pair:
                    name, value = pair.split(":", 1)
                    headers[name.strip()] = value.strip()
                    logger.debug(f"Added custom header: {name.strip()}")
            
            # Merge custom headers with existing default_headers
            if headers and "default_headers" in client_kwargs:
                client_kwargs["default_headers"].update(headers)
        except Exception as e:
            logger.warning(f"Failed to parse custom headers: {e}")
    
    # Create client
    client = OpenAI(**client_kwargs)
    
    return client

"""OpenAI client factory with support for company APIs using Basic authentication.

This module follows the official company API pattern:
1. Read credentials from environment variables
2. Encode username:password as Base64
3. Create OpenAI client with custom base_url and Authorization header
4. Return client for use with LangChain, LlamaIndex, or direct OpenAI SDK usage
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


def create_openai_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> OpenAI:
    """Create an OpenAI client with optional Basic authentication.
    
    This follows the company API pattern:
    - Encode username:password as Base64
    - Add Authorization: Basic <token> header
    - Use custom base_url for company APIs
    
    Args:
        api_key: API key (can be "xxxx" placeholder for company APIs)
        base_url: Custom base URL for company APIs (e.g., "https://genai.iais.fraunhofer.de/api/v2")
        username: Basic auth username
        password: Basic auth password
    
    Returns:
        Configured OpenAI client instance
        
    Raises:
        ImportError: If openai package is not installed
        ValueError: If required parameters are missing
    
    Example (company API):
        client = create_openai_client(
            api_key="xxxx",
            base_url="https://genai.iais.fraunhofer.de/api/v2",
            username="my-username",
            password="my-password"
        )
        
        # Use the client
        completion = client.chat.completions.create(
            model="Llama-3-SauerkrautLM",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    if OpenAI is None:
        raise ImportError(
            "openai package is not installed. Install it with: uv add openai"
        )
    
    settings = get_settings()
    api_key = api_key or (settings.openai_api_key if settings.openai_api_key and settings.openai_api_key.strip() else None) or "xxxx"
    base_url = base_url or (settings.openai_base_url if settings.openai_base_url and settings.openai_base_url.strip() else None)
    username = username or (settings.openai_auth_username if settings.openai_auth_username and settings.openai_auth_username.strip() else None)
    password = password or (settings.openai_auth_password if settings.openai_auth_password and settings.openai_auth_password.strip() else None)
    
    default_headers = {}
    if username and password:
        token_string = f"{username}:{password}"
        token_bytes = b64encode(token_string.encode())
        default_headers["Authorization"] = f"Basic {token_bytes.decode()}"
        
        logger.debug(
            f"Configured Basic authentication for OpenAI client "
            f"(base_url={base_url}, username={username})"
        )
    
    # Add custom headers for company APIs (if configured)
    # Note: extra_headers and extra_body are passed per-request in API calls
    # This only handles default headers that should be on every request
    settings = get_settings()
    if settings.company_api_extra_headers:
        try:
            # Parse format: "Header-Name:value" separated by commas
            header_pairs = settings.company_api_extra_headers.split(",")
            for pair in header_pairs:
                pair = pair.strip()
                if ":" in pair:
                    header_name, header_value = pair.split(":", 1)
                    default_headers[header_name.strip()] = header_value.strip()
                    logger.debug(f"Added custom header: {header_name.strip()}")
        except Exception as e:
            logger.warning(f"Failed to parse company_api_extra_headers: {e}")
    
    client = OpenAI(
        api_key=api_key,
        default_headers=default_headers if default_headers else None,
        base_url=base_url
    )
    
    return client


def get_openai_client() -> OpenAI:
    """Get a configured OpenAI client using settings from environment variables.
    
    This is the main entry point for getting an OpenAI client. It reads
    all configuration from settings (which reads from .env file) and creates
    a properly configured client.
    
    Returns:
        Configured OpenAI client ready for use
        
    Example:
        client = get_openai_client()
        completion = client.chat.completions.create(
            model="Llama-3-SauerkrautLM",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    settings = get_settings()
    return create_openai_client(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        username=settings.openai_auth_username,
        password=settings.openai_auth_password,
    )


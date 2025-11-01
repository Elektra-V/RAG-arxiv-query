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
    
    # Use default values from settings if not provided
    settings = get_settings()
    
    api_key = api_key or settings.openai_api_key or "xxxx"
    base_url = base_url or settings.openai_base_url
    username = username or settings.openai_auth_username
    password = password or settings.openai_auth_password
    
    # Build default headers for Basic auth if credentials provided
    default_headers = {}
    if username and password:
        # Follow official company API pattern: Base64 encode username:password
        token_string = f"{username}:{password}"
        token_bytes = b64encode(token_string.encode())
        default_headers["Authorization"] = f"Basic {token_bytes.decode()}"
        
        logger.debug(
            f"Configured Basic authentication for OpenAI client "
            f"(base_url={base_url}, username={username})"
        )
    
    # Create OpenAI client with custom configuration
    client_kwargs = {
        "api_key": api_key,
    }
    
    if base_url:
        client_kwargs["base_url"] = base_url
    
    if default_headers:
        client_kwargs["default_headers"] = default_headers
    
    client = OpenAI(**client_kwargs)
    
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


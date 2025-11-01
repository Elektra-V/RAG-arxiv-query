"""Embedding utilities."""

from base64 import b64encode
from functools import lru_cache

from langchain_core.embeddings import Embeddings

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None

from rag_api.settings import get_settings


@lru_cache
def get_embeddings() -> Embeddings:
    """Return a cached embedding model instance based on provider settings."""

    settings = get_settings()

    if settings.embedding_provider == "openai":
        if OpenAIEmbeddings is None:
            raise ImportError(
                "langchain-openai is not installed. Install it with: uv add langchain-openai"
            )
        # API key can be provided via env var OPENAI_API_KEY or explicitly
        api_key = settings.openai_api_key or "xxxx"  # Use placeholder if not set (for company APIs)
        
        # Build custom headers for company API Basic auth
        default_headers = {}
        if settings.openai_auth_username and settings.openai_auth_password:
            token_string = f"{settings.openai_auth_username}:{settings.openai_auth_password}"
            token_bytes = b64encode(token_string.encode())
            default_headers["Authorization"] = f"Basic {token_bytes.decode()}"
        
        # Create client kwargs
        client_kwargs = {
            "model": settings.openai_embedding_model,
            "api_key": api_key,
        }
        
        # Add custom base URL if provided (for company APIs)
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        
        # Add default headers if Basic auth is configured
        if default_headers:
            try:
                from openai import OpenAI
                openai_client = OpenAI(
                    api_key=api_key,
                    base_url=settings.openai_base_url or "https://api.openai.com/v1",
                    default_headers=default_headers,
                )
                client_kwargs["client"] = openai_client
            except ImportError:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    "Custom auth headers configured but 'openai' package not available. "
                    "Install 'openai' package to enable Basic auth support."
                )
        
        return OpenAIEmbeddings(**client_kwargs)

    elif settings.embedding_provider == "huggingface":
        if HuggingFaceEmbeddings is None:
            raise ImportError(
                "langchain-huggingface is not installed. Install it with: uv add langchain-huggingface"
            )
        return HuggingFaceEmbeddings(model_name=settings.huggingface_model)

    else:
        raise ValueError(
            f"Unsupported embedding provider: {settings.embedding_provider}. "
            "Supported providers: 'huggingface', 'openai'"
        )

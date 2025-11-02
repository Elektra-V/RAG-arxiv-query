"""Embedding utilities."""

import os
from functools import lru_cache
from base64 import b64encode

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
        
        # OpenAIEmbeddings creates its own async client internally
        # We need to pass api_key and base_url explicitly so async client has them
        # For Gateway mode, use placeholder "xxxx" for api_key (Basic auth header is used)
        from rag_api.clients.openai import get_openai_client
        openai_client = get_openai_client()
        
        # Extract base_url and determine api_key
        # For Gateway mode, api_key is "xxxx" (placeholder) - Basic auth header handles auth
        # For Platform mode, api_key comes from settings
        api_key = settings.openai_api_key or "xxxx"
        base_url = str(openai_client.base_url) if openai_client.base_url else settings.openai_base_url
        
        # Get default_headers from client if available (for Basic auth)
        default_headers = None
        if hasattr(openai_client, '_client'):
            default_headers = getattr(openai_client._client, 'default_headers', None)
        
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            client=openai_client,  # Sync client for sync operations
            openai_api_key=api_key,  # Required for async client creation (SDK validation)
            openai_api_base=base_url,  # Required for async client to use correct endpoint
        )

    elif settings.embedding_provider == "huggingface":
        if HuggingFaceEmbeddings is None:
            raise ImportError(
                "langchain-huggingface is not installed. Install it with: uv add langchain-huggingface"
            )
        # Force CPU usage to avoid CUDA compatibility issues
        # Set environment variable to prevent CUDA initialization
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        # Set device explicitly to CPU via model_kwargs
        return HuggingFaceEmbeddings(
            model_name=settings.huggingface_model,
            model_kwargs={"device": "cpu"}
        )

    else:
        raise ValueError(
            f"Unsupported embedding provider: {settings.embedding_provider}. "
            "Supported providers: 'huggingface', 'openai'"
        )

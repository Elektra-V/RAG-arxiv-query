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
        
        # OpenAIEmbeddings needs api_key, base_url, and default_headers
        # Gateway doesn't support encoding_format='base64' parameter
        # Use client parameter and override embedding creation to remove encoding_format
        from rag_api.clients.openai import get_openai_client
        openai_client = get_openai_client()
        
        # Create OpenAIEmbeddings with client to control embedding creation
        # We'll need to handle encoding_format removal via client monkey-patch or subclass
        api_key = settings.openai_api_key or "xxxx"
        base_url = settings.openai_base_url
        
        # Build Basic auth header for default_headers (if Gateway mode)
        default_headers = None
        if settings.openai_auth_username and settings.openai_auth_password:
            token_string = f"{settings.openai_auth_username}:{settings.openai_auth_password}"
            token_bytes = b64encode(token_string.encode())
            default_headers = {"Authorization": f"Basic {token_bytes.decode()}"}
        
        # Create embeddings instance
        embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=api_key,  # Placeholder "xxxx" for Gateway (Basic auth used)
            openai_api_base=base_url,  # Gateway endpoint
            default_headers=default_headers,  # Basic auth header
            client=openai_client,  # Use our configured client
        )
        
        # Override the embeddings.client.embeddings.create to remove encoding_format
        # Gateway doesn't support encoding_format='base64' parameter
        original_create = embeddings.client.embeddings.create
        
        def create_without_encoding_format(*args, **kwargs):
            # Remove encoding_format if present (gateway doesn't support it)
            if 'encoding_format' in kwargs:
                del kwargs['encoding_format']
            return original_create(*args, **kwargs)
        
        embeddings.client.embeddings.create = create_without_encoding_format
        
        return embeddings

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

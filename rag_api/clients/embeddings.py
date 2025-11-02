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
        
        # Gateway requirements:
        # 1. Needs Basic auth in default_headers
        # 2. Doesn't support encoding_format='base64' (must be removed)
        # 3. Input must be text strings, not token IDs (disable tokenization)
        
        api_key = settings.openai_api_key or "xxxx"
        base_url = settings.openai_base_url
        
        # Build Basic auth header
        default_headers = None
        if settings.openai_auth_username and settings.openai_auth_password:
            token_string = f"{settings.openai_auth_username}:{settings.openai_auth_password}"
            token_bytes = b64encode(token_string.encode())
            default_headers = {"Authorization": f"Basic {token_bytes.decode()}"}
        
        # Create embeddings with gateway-compatible settings
        embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            default_headers=default_headers,
            tiktoken_enabled=False,  # Gateway needs text, not token IDs
        )
        
        # Patch create method: Remove encoding_format and ensure input format
        # Gateway requirements:
        # - input must be list: ["text"] not "text"
        # - response.data[0].embedding (singular, not embeddings)
        if hasattr(embeddings.client, 'create'):
            original_create = embeddings.client.create
            
            def create_fixed(**kwargs):
                kwargs.pop('encoding_format', None)  # Gateway doesn't support this
                
                # Ensure input is always a list (gateway requirement)
                if 'input' in kwargs and isinstance(kwargs['input'], str):
                    kwargs['input'] = [kwargs['input']]
                
                return original_create(**kwargs)
            
            embeddings.client.create = create_fixed
        
        # Patch async client too
        if hasattr(embeddings, 'async_client') and hasattr(embeddings.async_client, 'create'):
            original_async_create = embeddings.async_client.create
            
            def create_async_fixed(**kwargs):
                kwargs.pop('encoding_format', None)
                if 'input' in kwargs and isinstance(kwargs['input'], str):
                    kwargs['input'] = [kwargs['input']]
                return original_async_create(**kwargs)
            
            embeddings.async_client.create = create_async_fixed
        
        return embeddings

    elif settings.embedding_provider == "huggingface":
        if HuggingFaceEmbeddings is None:
            raise ImportError(
                "langchain-huggingface is not installed. Install it with: uv add langchain-huggingface"
            )
        
        # Validate model name - ensure it's not a gateway/OpenAI model name
        model_name = settings.huggingface_model
        gateway_model_names = ["all-mpnet-base-v2", "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
        if model_name in gateway_model_names:
            raise ValueError(
                f"Error: '{model_name}' is a gateway/OpenAI embedding model, not a HuggingFace model.\n"
                f"\n"
                f"For gateway embeddings (all-mpnet-base-v2) via Fraunhofer gateway:\n"
                f"  Set EMBEDDING_PROVIDER='openai' (not 'huggingface')\n"
                f"  Set OPENAI_EMBEDDING_MODEL='all-mpnet-base-v2' (per company API docs)\n"
                f"\n"
                f"For local HuggingFace embeddings:\n"
                f"  Set EMBEDDING_PROVIDER='huggingface'\n"
                f"  Set HUGGINGFACE_MODEL='sentence-transformers/all-MiniLM-L6-v2'"
            )
        
        # Force CPU usage to avoid CUDA compatibility issues
        # Set environment variable to prevent CUDA initialization
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        # Set device explicitly to CPU via model_kwargs
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"}
        )

    else:
        raise ValueError(
            f"Unsupported embedding provider: {settings.embedding_provider}. "
            "Supported providers: 'huggingface', 'openai'"
        )

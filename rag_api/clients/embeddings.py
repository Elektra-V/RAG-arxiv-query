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
        # We need to wrap the embedding creation to remove this parameter
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
        )
        
        # Gateway requirements:
        # 1. Doesn't support encoding_format='base64' parameter  
        # 2. Input must be a list of text strings (not token IDs)
        # 3. LangChain's _tokenize converts text to token IDs [[1985]], but gateway needs raw text
        # Solution: Override _tokenize to return text directly, and patch create to remove encoding_format
        
        # Disable tokenization - gateway needs raw text, not token IDs
        embeddings.tiktoken_enabled = False
        
        # Override _tokenize to return text directly (not token IDs)
        # LangChain's default _tokenize converts text to token IDs, but gateway needs text
        original_tokenize = embeddings._tokenize
        
        def tokenize_text_only(texts: list[str], chunk_size: int):
            """Tokenize that returns text directly (not token IDs) for gateway compatibility."""
            # Return texts as-is with indices - gateway handles tokenization
            indices = list(range(len(texts)))
            return texts, [], indices  # texts, tokens (empty), indices
        
        embeddings._tokenize = tokenize_text_only
        
        # Patch embeddings.create to remove encoding_format and ensure input format
        if hasattr(embeddings, 'client') and hasattr(embeddings.client, 'embeddings'):
            original_create = embeddings.client.embeddings.create
            
            def create_gateway_compatible(**kwargs):
                # Remove encoding_format (gateway doesn't support it)
                kwargs.pop('encoding_format', None)
                
                # Ensure input is a list of strings (gateway requirement)
                if 'input' in kwargs:
                    input_val = kwargs['input']
                    if isinstance(input_val, str):
                        kwargs['input'] = [input_val]
                    elif isinstance(input_val, list):
                        # Convert any token IDs or nested lists to strings
                        fixed_input = []
                        for item in input_val:
                            if isinstance(item, str):
                                fixed_input.append(item)
                            elif isinstance(item, list):
                                # Nested list of token IDs - join as string (fallback)
                                fixed_input.append(' '.join(str(i) for i in item))
                            elif isinstance(item, (int, float)):
                                fixed_input.append(str(item))
                            else:
                                fixed_input.append(str(item))
                        kwargs['input'] = fixed_input
                    else:
                        kwargs['input'] = [str(input_val)]
                
                return original_create(**kwargs)
            
            embeddings.client.embeddings.create = create_gateway_compatible
            
            # Patch async client too
            if hasattr(embeddings, 'async_client') and hasattr(embeddings.async_client, 'embeddings'):
                original_async_create = embeddings.async_client.embeddings.create
                
                def create_async_gateway_compatible(**kwargs):
                    kwargs.pop('encoding_format', None)
                    if 'input' in kwargs:
                        input_val = kwargs['input']
                        if isinstance(input_val, str):
                            kwargs['input'] = [input_val]
                        elif isinstance(input_val, list):
                            fixed_input = []
                            for item in input_val:
                                if isinstance(item, str):
                                    fixed_input.append(item)
                                elif isinstance(item, list):
                                    fixed_input.append(' '.join(str(i) for i in item))
                                elif isinstance(item, (int, float)):
                                    fixed_input.append(str(item))
                                else:
                                    fixed_input.append(str(item))
                            kwargs['input'] = fixed_input
                        else:
                            kwargs['input'] = [str(input_val)]
                    return original_async_create(**kwargs)
                
                embeddings.async_client.embeddings.create = create_async_gateway_compatible
        
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

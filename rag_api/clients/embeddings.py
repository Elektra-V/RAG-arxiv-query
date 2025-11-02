"""Embedding utilities."""

import logging
import os
from functools import lru_cache
from base64 import b64encode
from typing import Optional

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

logger = logging.getLogger(__name__)


def _is_qwen_model(model_name: str) -> bool:
    """Check if the model name is a Qwen model.
    
    Args:
        model_name: The LLM model name (e.g., "Qwen2.5-7B-Instruct")
        
    Returns:
        True if the model is a Qwen model, False otherwise
    """
    if not model_name:
        return False
    return model_name.lower().startswith("qwen")


def _get_embedding_model_for_llm(
    llm_model: str,
    user_override: Optional[str] = None
) -> str:
    """Automatically select the appropriate embedding model based on LLM model.
    
    Rules:
    - Qwen LLM models require Qwen-compatible embedding models
    - Non-Qwen models use all-mpnet-base-v2 (gateway default)
    - User override via OPENAI_EMBEDDING_MODEL takes precedence
    
    Args:
        llm_model: The LLM model name (e.g., "Qwen2.5-7B-Instruct")
        user_override: Manual embedding model override from settings (optional)
        
    Returns:
        The embedding model name to use
    """
    # User override takes precedence
    if user_override:
        return user_override
    
    # Auto-detect based on LLM model
    if _is_qwen_model(llm_model):
        # Qwen models should use text-embedding-3-small or text-embedding-3-large
        # (No separate Qwen-specific embedding models available on gateway)
        # Using text-embedding-3-small as default for Qwen models
        embedding_model = "text-embedding-3-small"
        
        logger.info(
            f"Auto-detected Qwen LLM model '{llm_model}' - using embedding model "
            f"'{embedding_model}'. "
            f"Alternative: Use 'text-embedding-3-large' for better quality."
        )
        return embedding_model
    else:
        # Non-Qwen models use all-mpnet-base-v2_t2e (note the _t2e suffix)
        # Gateway has: all-mpnet-base-v2_t2e (not all-mpnet-base-v2)
        embedding_model = "all-mpnet-base-v2_t2e"
        logger.debug(
            f"Non-Qwen LLM model '{llm_model}' - using gateway embedding model "
            f"'{embedding_model}'"
        )
        return embedding_model


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
        
        # Auto-detect embedding model based on LLM model
        # Qwen models require Qwen-compatible embeddings
        embedding_model = _get_embedding_model_for_llm(
            llm_model=settings.openai_model,
            user_override=settings.openai_embedding_model
        )
        
        # Validate compatibility if user manually set embedding model
        if settings.openai_embedding_model and settings.openai_embedding_model != embedding_model:
            is_qwen_llm = _is_qwen_model(settings.openai_model)
            is_qwen_embedding = _is_qwen_model(settings.openai_embedding_model)
            
            if is_qwen_llm and not is_qwen_embedding:
                logger.warning(
                    f"⚠️  Model mismatch detected: Qwen LLM model '{settings.openai_model}' "
                    f"with non-Qwen embedding model '{settings.openai_embedding_model}'. "
                    f"Qwen models require Qwen-compatible embeddings. "
                    f"Consider removing OPENAI_EMBEDDING_MODEL to auto-detect."
                )
            elif not is_qwen_llm and is_qwen_embedding:
                logger.warning(
                    f"⚠️  Model mismatch detected: Non-Qwen LLM model '{settings.openai_model}' "
                    f"with Qwen embedding model '{settings.openai_embedding_model}'. "
                    f"Using user override, but this may not be optimal."
                )
        else:
            # Using auto-detected model
            logger.debug(
                f"Using embedding model '{embedding_model}' for LLM '{settings.openai_model}'"
            )
        
        base_url = settings.openai_base_url
        
        # Build Basic auth header
        default_headers = None
        has_basic_auth = settings.openai_auth_username and settings.openai_auth_password
        
        if has_basic_auth:
            token_string = f"{settings.openai_auth_username}:{settings.openai_auth_password}"
            token_bytes = b64encode(token_string.encode())
            default_headers = {"Authorization": f"Basic {token_bytes.decode()}"}
        
        # For Basic auth, use empty string for api_key (SDK validation, but Basic auth takes precedence)
        # For Platform mode, use the provided API key
        # Note: SDK may require api_key parameter, but Basic auth header will be used
        if has_basic_auth:
            # Basic auth mode: Use empty string to satisfy SDK validation
            # The default_headers with Basic auth will actually be used
            api_key = ""
        else:
            # Platform mode: Use actual API key
            api_key = settings.openai_api_key or "xxxx"
        
        # Create embeddings with gateway-compatible settings
        embeddings = OpenAIEmbeddings(
            model=embedding_model,  # Use auto-detected or user override
            openai_api_key=api_key if api_key else None,  # Empty string or None for Basic auth
            openai_api_base=base_url,
            default_headers=default_headers,
            tiktoken_enabled=False,  # Gateway needs text, not token IDs
            check_embedding_ctx_length=False,  # Disable length checking to avoid HuggingFace tokenizer fallback
        )
        
        # Patch to remove encoding_format from request body (gateway doesn't support it)
        # The SDK adds encoding_format internally via parameter models, so we intercept at request level
        # We need to patch both the Embeddings resource's _post AND the underlying OpenAI client's _post
        embeddings_resource = embeddings.client
        
        def remove_encoding_format_from_request(*args, **kwargs):
            """Helper to remove encoding_format from request in multiple possible locations."""
            # Check if json_data is passed directly as kwarg
            if 'json_data' in kwargs and isinstance(kwargs['json_data'], dict):
                kwargs['json_data'].pop('encoding_format', None)
            # Also check if it's in the body directly (some SDK versions)
            if 'body' in kwargs and isinstance(kwargs['body'], dict):
                kwargs['body'].pop('encoding_format', None)
            # Check if json_data is in a FinalRequestOptions object (first positional arg)
            if args and hasattr(args[0], 'json_data') and isinstance(args[0].json_data, dict):
                args[0].json_data.pop('encoding_format', None)
        
        # Patch the Embeddings resource's _post method (embeddings.client._post)
        if hasattr(embeddings_resource, '_post'):
            original_resource_post = embeddings_resource._post
            
            def resource_post_fixed(*args, **kwargs):
                remove_encoding_format_from_request(*args, **kwargs)
                return original_resource_post(*args, **kwargs)
            
            embeddings_resource._post = resource_post_fixed
        
        # Get the underlying OpenAI client and patch its _post method too
        openai_client = None
        if hasattr(embeddings_resource, '_client'):
            openai_client = embeddings_resource._client
        elif hasattr(embeddings, '_client'):
            openai_client = embeddings._client
        
        if openai_client and hasattr(openai_client, '_post'):
            original_post = openai_client._post
            
            def post_fixed(*args, **kwargs):
                remove_encoding_format_from_request(*args, **kwargs)
                return original_post(*args, **kwargs)
            
            openai_client._post = post_fixed
        
        # Patch create method: Remove encoding_format from kwargs and ensure input format
        # Gateway requirements:
        # - input must be list: ["text"] not "text"
        # - encoding_format must be removed (also patched at _post level)
        if hasattr(embeddings.client, 'create'):
            original_create = embeddings.client.create
            
            def create_fixed(**kwargs):
                kwargs.pop('encoding_format', None)  # Remove from kwargs
                
                # Ensure input is always a list (gateway requirement)
                if 'input' in kwargs and isinstance(kwargs['input'], str):
                    kwargs['input'] = [kwargs['input']]
                
                return original_create(**kwargs)
            
            embeddings.client.create = create_fixed
        
        # Patch async client too
        if hasattr(embeddings, 'async_client') and hasattr(embeddings.async_client, 'create'):
            async_embeddings_resource = embeddings.async_client
            
            async def remove_encoding_format_from_async_request(*args, **kwargs):
                """Helper to remove encoding_format from async request."""
                # Check if json_data is passed directly as kwarg
                if 'json_data' in kwargs and isinstance(kwargs['json_data'], dict):
                    kwargs['json_data'].pop('encoding_format', None)
                # Check if it's in the body directly (some SDK versions)
                if 'body' in kwargs and isinstance(kwargs['body'], dict):
                    kwargs['body'].pop('encoding_format', None)
                # Check if json_data is in a FinalRequestOptions object (first positional arg)
                if args and hasattr(args[0], 'json_data') and isinstance(args[0].json_data, dict):
                    args[0].json_data.pop('encoding_format', None)
            
            # Patch the async Embeddings resource's _post method
            if hasattr(async_embeddings_resource, '_post'):
                original_async_resource_post = async_embeddings_resource._post
                
                async def async_resource_post_fixed(*args, **kwargs):
                    await remove_encoding_format_from_async_request(*args, **kwargs)
                    return await original_async_resource_post(*args, **kwargs)
                
                async_embeddings_resource._post = async_resource_post_fixed
            
            # Get the underlying async OpenAI client and patch its _post method too
            async_openai_client = None
            if hasattr(async_embeddings_resource, '_client'):
                async_openai_client = async_embeddings_resource._client
            elif hasattr(embeddings, '_async_client'):
                async_openai_client = embeddings._async_client
            
            if async_openai_client and hasattr(async_openai_client, '_post'):
                original_async_post = async_openai_client._post
                
                async def async_post_fixed(*args, **kwargs):
                    await remove_encoding_format_from_async_request(*args, **kwargs)
                    return await original_async_post(*args, **kwargs)
                
                async_openai_client._post = async_post_fixed
            
            # Patch async create method
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
        gateway_model_names = [
            "all-mpnet-base-v2_t2e",
            "all-mpnet-base-v2",
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002"
        ]
        if model_name in gateway_model_names:
            raise ValueError(
                f"Error: '{model_name}' is a gateway embedding model, not a HuggingFace model.\n"
                f"\n"
                f"For gateway embeddings via Fraunhofer gateway:\n"
                f"  Set EMBEDDING_PROVIDER='openai' (not 'huggingface')\n"
                f"  Set OPENAI_EMBEDDING_MODEL='{model_name}' or leave empty for auto-detection\n"
                f"\n"
                f"Available gateway embedding models:\n"
                f"  - all-mpnet-base-v2_t2e (for non-Qwen models)\n"
                f"  - text-embedding-3-small (for Qwen models, recommended)\n"
                f"  - text-embedding-3-large (for Qwen models, higher quality)\n"
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

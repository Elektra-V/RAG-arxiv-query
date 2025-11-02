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
        # Qwen models need Qwen-compatible embeddings
        # Common patterns (verify with company API docs):
        # - qwen2.5-embedding
        # - qwen2.5-vl-embedding (for VL models)
        # - qwen2-embedding
        
        # For now, use a pattern-based approach
        llm_lower = llm_model.lower()
        if "vl" in llm_lower or "vision" in llm_lower:
            # VL models might need specific embeddings
            embedding_model = "qwen2.5-vl-embedding"
        elif "2.5" in llm_lower:
            embedding_model = "qwen2.5-embedding"
        elif "2" in llm_lower:
            embedding_model = "qwen2-embedding"
        else:
            # Fallback for other Qwen variants
            embedding_model = "qwen2.5-embedding"
        
        logger.info(
            f"Auto-detected Qwen LLM model '{llm_model}' - using Qwen-compatible "
            f"embedding model '{embedding_model}'. "
            f"If this fails, verify the exact model name in company API docs."
        )
        return embedding_model
    else:
        # Non-Qwen models use gateway default
        embedding_model = "all-mpnet-base-v2"
        logger.debug(
            f"Non-Qwen LLM model '{llm_model}' - using default embedding model "
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
            model=embedding_model,  # Use auto-detected or user override
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

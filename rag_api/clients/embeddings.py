"""Embedding utilities."""

import logging
import os
from functools import lru_cache
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


def _get_embedding_model_for_llm(
    llm_model: str,
    user_override: Optional[str] = None
) -> str:
    """Automatically select the appropriate embedding model based on LLM model.
    
    Defaults to text-embedding-3-small for OpenAI models.
    
    Args:
        llm_model: The LLM model name
        user_override: Manual embedding model override from settings (optional)
        
    Returns:
        The embedding model name to use
    """
    # User override takes precedence
    if user_override:
        return user_override
    
    # Default for OpenAI Platform
    embedding_model = "text-embedding-3-small"
    logger.debug(
        f"Using embedding model '{embedding_model}' for LLM '{llm_model}'"
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
        
        # Auto-detect embedding model based on LLM model
        embedding_model = _get_embedding_model_for_llm(
            llm_model=settings.openai_model,
            user_override=settings.openai_embedding_model
        )
        
        # Create embeddings with OpenAI Platform
        embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=settings.openai_api_key,
        )
        
        return embeddings

    elif settings.embedding_provider == "huggingface":
        if HuggingFaceEmbeddings is None:
            raise ImportError(
                "langchain-huggingface is not installed. Install it with: uv add langchain-huggingface"
            )
        
        # Force CPU usage to avoid CUDA compatibility issues
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        return HuggingFaceEmbeddings(
            model_name=settings.huggingface_model,
            model_kwargs={"device": "cpu"}
        )

    else:
        raise ValueError(
            f"Unsupported embedding provider: {settings.embedding_provider}. "
            "Supported providers: 'huggingface', 'openai'"
        )

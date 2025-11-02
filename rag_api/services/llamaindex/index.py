"""Helpers for building LlamaIndex service components."""

from __future__ import annotations

from functools import lru_cache

from llama_index.core import Settings as LISettings
from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM

try:
    from llama_index.embeddings.openai import OpenAIEmbedding
except ImportError:
    OpenAIEmbedding = None

try:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
except ImportError:
    HuggingFaceEmbedding = None

try:
    from llama_index.llms.openai import OpenAI
except ImportError:
    OpenAI = None

from llama_index.vector_stores.qdrant import QdrantVectorStore

from rag_api.clients.openai import get_openai_client
from rag_api.clients.qdrant import get_qdrant_client
from rag_api.settings import get_settings


def get_llamaindex_embedding() -> BaseEmbedding:
    """Get the configured embedding model based on provider settings."""
    settings = get_settings()

    if settings.embedding_provider == "openai":
        if OpenAIEmbedding is None:
            raise ImportError(
                "llama-index-embeddings-openai is not installed. "
                "Install it with: uv add llama-index-embeddings-openai"
            )
        
        # Use the centralized OpenAI client factory
        openai_client = get_openai_client()
        
        # Auto-detect embedding model if not set
        embedding_model = settings.openai_embedding_model or "text-embedding-3-small"
        
        return OpenAIEmbedding(
            model=embedding_model,
            client=openai_client,
        )

    elif settings.embedding_provider == "huggingface":
        if HuggingFaceEmbedding is None:
            raise ImportError(
                "llama-index-embeddings-huggingface is not installed. "
                "Install it with: uv add llama-index-embeddings-huggingface"
            )
        # Force CPU usage to avoid CUDA compatibility issues
        import os
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        return HuggingFaceEmbedding(
            model_name=settings.huggingface_model,
            device="cpu"
        )

    else:
        raise ValueError(
            f"Unsupported embedding provider: {settings.embedding_provider}. "
            "Supported providers: 'huggingface', 'openai'"
        )


def get_llamaindex_llm() -> LLM:
    """Get the configured LLM model for OpenAI Platform."""
    settings = get_settings()

    if OpenAI is None:
        raise ImportError(
            "llama-index-llms-openai is not installed. "
            "Install it with: uv add llama-index-llms-openai"
        )
    
    openai_client = get_openai_client()
    return OpenAI(
        model=settings.openai_model,
        client=openai_client,
        temperature=0,
    )


@lru_cache
def configure_llamaindex() -> None:
    """Configure global LlamaIndex settings."""

    settings = get_settings()
    LISettings.embed_model = get_llamaindex_embedding()
    LISettings.llm = get_llamaindex_llm()


@lru_cache
def get_index() -> VectorStoreIndex:
    """Return a cached VectorStoreIndex backed by Qdrant."""

    configure_llamaindex()
    settings = get_settings()
    qdrant_client = get_qdrant_client()

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=settings.qdrant_collection,
    )

    return VectorStoreIndex.from_vector_store(vector_store=vector_store)

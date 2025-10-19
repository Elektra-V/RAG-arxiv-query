"""Helpers for building LlamaIndex service components."""

from __future__ import annotations

from functools import lru_cache

from llama_index.core import Settings as LISettings
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.qdrant import QdrantVectorStore

from rag_api.clients.qdrant import get_qdrant_client
from rag_api.settings import get_settings


@lru_cache
def configure_llamaindex() -> None:
    """Configure global LlamaIndex settings."""

    settings = get_settings()
    LISettings.embed_model = HuggingFaceEmbedding(model_name=settings.huggingface_model)
    LISettings.llm = Ollama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        request_timeout=120.0,
    )


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

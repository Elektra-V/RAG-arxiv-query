"""Embedding utilities."""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from rag_api.settings import get_settings


@lru_cache
def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached embedding model instance."""

    settings = get_settings()
    return HuggingFaceEmbeddings(model_name=settings.huggingface_model)

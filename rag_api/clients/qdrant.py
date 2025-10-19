"""Qdrant client utilities."""

from functools import lru_cache

from qdrant_client import QdrantClient

from rag_api.settings import get_settings


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Return a cached Qdrant client instance."""

    settings = get_settings()
    return QdrantClient(url=settings.qdrant_url)

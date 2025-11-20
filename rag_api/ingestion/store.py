"""Utilities for storing documents in Qdrant."""

from __future__ import annotations

import uuid
from typing import Iterable

from langchain_core.documents import Document
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from rag_api.clients.embeddings import get_embeddings
from rag_api.clients.qdrant import get_qdrant_client
from rag_api.settings import get_settings


def _get_embedding_dimension() -> int:
    """Get the dimension size for the current embedding model."""
    settings = get_settings()
    embeddings = get_embeddings()
    
    # Get dimension by embedding a test string
    test_embedding = embeddings.embed_query("test")
    return len(test_embedding)


def ensure_collection() -> None:
    """Ensure target Qdrant collection exists with correct vector dimensions."""

    settings = get_settings()
    client = get_qdrant_client()
    collections = client.get_collections().collections
    names = [collection.name for collection in collections]

    if settings.qdrant_collection in names:
        collection_info = client.get_collection(settings.qdrant_collection)
        current_size = collection_info.config.params.vectors.size if collection_info.config.params.vectors else 384
        expected_size = _get_embedding_dimension()
        if current_size != expected_size:
            raise ValueError(
                f"Collection '{settings.qdrant_collection}' has dimension {current_size}, "
                f"but current embedding model requires {expected_size}. "
                "Please delete the collection or use a different collection name."
            )
        return

    dimension = _get_embedding_dimension()
    client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
    )


def upsert_documents(documents: Iterable[Document]) -> int:
    """Embed and upsert documents into Qdrant, returning count processed."""

    settings = get_settings()
    embeddings = get_embeddings()
    client = get_qdrant_client()

    payloads = []
    for document in documents:
        payloads.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embeddings.embed_query(document.page_content),
                payload={
                    "text": document.page_content,
                    "metadata": document.metadata,
                },
            )
        )

    if payloads:
        client.upsert(collection_name=settings.qdrant_collection, points=payloads)

    return len(payloads)

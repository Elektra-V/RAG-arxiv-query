"""Utilities for storing documents in Qdrant."""

from __future__ import annotations

import uuid
from typing import Iterable

from langchain_core.documents import Document
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from rag_api.clients.embeddings import get_embeddings
from rag_api.clients.qdrant import get_qdrant_client
from rag_api.settings import get_settings


def ensure_collection() -> None:
    """Ensure target Qdrant collection exists."""

    settings = get_settings()
    client = get_qdrant_client()
    collections = client.get_collections().collections
    names = [collection.name for collection in collections]

    if settings.qdrant_collection in names:
        return

    client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
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

"""Reusable ingestion pipeline helpers."""

from __future__ import annotations

import logging
from typing import Iterable

from langchain_core.documents import Document

from rag_api.ingestion.arxiv import load_documents
from rag_api.ingestion.store import ensure_collection, upsert_documents

LOGGER = logging.getLogger(__name__)


def _ensure_iterable(documents: Iterable[Document] | None) -> list[Document]:
    if not documents:
        return []
    if isinstance(documents, list):
        return documents
    return list(documents)


def run_ingestion(query: str, max_docs: int) -> dict[str, int | str]:
    """Execute the ingestion flow and return summary metadata."""

    ensure_collection()

    docs = load_documents(query, max_docs)
    documents = _ensure_iterable(docs)

    if not documents:
        LOGGER.info("No documents retrieved for query '%s'", query)
        return {"ingested": 0, "query": query}

    count = upsert_documents(documents)
    LOGGER.info("Ingested %s documents for query '%s'", count, query)
    return {"ingested": count, "query": query}

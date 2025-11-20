"""Utilities for loading arXiv documents."""

from __future__ import annotations

from typing import List
from xml.etree import ElementTree as ET

import requests
from langchain_community.document_loaders import ArxivLoader
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    import fitz
    if not hasattr(fitz, "fitz"):
        setattr(fitz, "fitz", fitz)
except ImportError:
    pass


def _fetch_via_api(query: str, max_docs: int) -> List[Document]:
    """Fallback loader using the public arXiv API."""

    api_url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_docs,
    }
    response = requests.get(api_url, params=params, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    documents: List[Document] = []

    for entry in entries[:max_docs]:
        title = entry.find("{http://www.w3.org/2005/Atom}title")
        summary = entry.find("{http://www.w3.org/2005/Atom}summary")
        identifier = entry.find("{http://www.w3.org/2005/Atom}id")

        doc_title = title.text if title is not None else "Untitled"
        doc_summary = summary.text if summary is not None else ""
        doc_id = identifier.text.split("/")[-1] if identifier is not None else "unknown"

        documents.append(
            Document(
                page_content=doc_summary.strip(),
                metadata={
                    "title": doc_title.strip(),
                    "arxiv_id": doc_id,
                    "source": f"https://arxiv.org/abs/{doc_id}",
                },
            )
        )

    return documents


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def load_documents(query: str, max_docs: int) -> List[Document]:
    """Load arXiv documents using the API (ArxivLoader doesn't support max_docs parameter)."""
    return _fetch_via_api(query, max_docs)

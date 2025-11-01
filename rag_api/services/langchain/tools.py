"""Tool definitions for the LangChain agent."""

from __future__ import annotations

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

from rag_api.clients.embeddings import get_embeddings
from rag_api.clients.qdrant import get_qdrant_client
from rag_api.settings import get_settings


@tool
def rag_query(query: str) -> str:
    """Query the Arxiv Qdrant collection for relevant chunks."""

    settings = get_settings()
    embeddings = get_embeddings()
    client = get_qdrant_client()

    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=embeddings.embed_query(query),
        limit=4,
    )

    if not results:
        return "RAG_EMPTY: No matching documents found in the knowledge base."

    formatted = []
    for match in results:
        metadata = match.payload.get("metadata", {}) if match.payload else {}
        title = metadata.get("title", "Untitled")
        source = metadata.get("source", "Unknown")
        text = match.payload.get("text", "") if match.payload else ""
        formatted.append(f"[DB: {title}] ({source})\n{text}")

    return "\n\n".join(formatted)


def get_tools() -> list:
    """Return list of tools available to the agent."""

    settings = get_settings()
    web_search = DuckDuckGoSearchRun(max_results=settings.duckduckgo_results)
    return [rag_query, web_search]

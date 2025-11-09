"""Tool definitions for the LangChain agent."""

from __future__ import annotations

import logging
from xml.etree import ElementTree as ET

import requests
from langchain_core.tools import tool

from rag_api.clients.embeddings import get_embeddings
from rag_api.clients.qdrant import get_qdrant_client
from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


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


@tool
def arxiv_search(query: str, max_results: int = 5) -> str:
    """Search arXiv directly via API for research papers.
    
    Use this when:
    - rag_query returns no results or insufficient context
    - You need to search broader arXiv coverage
    - You need recent papers not yet ingested into the knowledge base
    
    Args:
        query: Search query for arXiv (e.g., "quantum computing", "cat:cs.AI", "all:machine learning")
        max_results: Maximum number of papers to return (default: 5)
    
    Returns:
        Formatted string with paper titles, IDs, summaries, and links.
        Returns error message if search fails.
    """
    settings = get_settings()
    # Use the smaller of user-provided max_results or configured limit
    effective_max_results = min(max_results, settings.arxiv_search_max_results)
    
    try:
        api_url = "https://export.arxiv.org/api/query"
        params = {
            "search_query": query,
            "start": 0,
            "max_results": effective_max_results,
        }
        
        logger.debug(f"Searching arXiv with query: {query}, max_results: {effective_max_results}")
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        
        if not entries:
            return f"ARXIV_EMPTY: No papers found for query '{query}' on arXiv."
        
        formatted = []
        for entry in entries[:effective_max_results]:
            title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
            summary_elem = entry.find("{http://www.w3.org/2005/Atom}summary")
            identifier_elem = entry.find("{http://www.w3.org/2005/Atom}id")
            
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled"
            summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else "No summary available"
            arxiv_id = identifier_elem.text.split("/")[-1] if identifier_elem is not None and identifier_elem.text else "unknown"
            link = f"https://arxiv.org/abs/{arxiv_id}"
            
            # Truncate summary if too long
            summary_short = summary[:500] + "..." if len(summary) > 500 else summary
            
            formatted.append(
                f"[arXiv: {title}]\n"
                f"ID: {arxiv_id}\n"
                f"Summary: {summary_short}\n"
                f"Link: {link}"
            )
        
        return "\n\n---\n\n".join(formatted)
        
    except requests.RequestException as exc:
        error_msg = f"ARXIV_ERROR: Failed to search arXiv API: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        return error_msg
    except ET.ParseError as exc:
        error_msg = f"ARXIV_ERROR: Failed to parse arXiv API response: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        return error_msg
    except Exception as exc:
        error_msg = f"ARXIV_ERROR: Unexpected error during arXiv search: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


def get_tools() -> list:
    """Return list of tools available to the agent."""

    return [rag_query, arxiv_search]

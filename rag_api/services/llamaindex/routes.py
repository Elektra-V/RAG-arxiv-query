"""Router for LlamaIndex service."""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from rag_api.services.llamaindex.index import get_index
from rag_api.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    debug: bool = Field(default=True, description="Include debug information in response")
    similarity_top_k: int = Field(default=3, ge=1, le=10, description="Number of similar documents to retrieve")


class QueryResponse(BaseModel):
    answer: str
    debug: dict[str, Any] = Field(default_factory=dict, description="Debug information")
    status: str = Field(default="success", description="Response status")


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """Query the LlamaIndex RAG with optional debug information."""
    settings = get_settings()
    start_time = time.time()

    try:
        logger.info(f"Processing query: {request.question[:100]}...")
        
    index = get_index()
    query_engine = index.as_query_engine(
            similarity_top_k=request.similarity_top_k,
        response_mode="compact",
        summary_mode="tree_summarize",
    )
    response = query_engine.query(request.question)
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Extract debug info
        debug_info = {}
        if request.debug:
            debug_info = {
                "model_provider": settings.llm_provider,
                "embedding_provider": settings.embedding_provider,
                "similarity_top_k": request.similarity_top_k,
                "execution_time_ms": round(execution_time, 2),
            }
            
            # Try to extract source nodes if available
            if hasattr(response, "source_nodes") and response.source_nodes:
                debug_info["sources_found"] = len(response.source_nodes)
                debug_info["source_nodes"] = [
                    {
                        "score": getattr(node, "score", None),
                        "node_id": getattr(node, "node_id", None),
                    }
                    for node in response.source_nodes[:3]  # Limit to first 3
                ]
            
            # Try to extract metadata if available
            if hasattr(response, "metadata"):
                debug_info["metadata"] = response.metadata
        
        logger.info(f"Query processed successfully in {execution_time:.2f}ms")
        
        return QueryResponse(answer=str(response), debug=debug_info, status="success")
        
    except Exception as exc:
        logger.error(f"Error processing query: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(exc)}") from exc


@router.get("/status")
async def status() -> dict[str, Any]:
    """Get service status and configuration."""
    settings = get_settings()
    
    status_info = {
        "service": "llamaindex-rag-api",
        "status": "healthy",
        "configuration": {
            "llm_provider": settings.llm_provider,
            "embedding_provider": settings.embedding_provider,
            "qdrant_url": settings.qdrant_url,
            "collection": settings.qdrant_collection,
        },
    }
    
    # Check Qdrant connection
    try:
        from rag_api.clients.qdrant import get_qdrant_client
        client = get_qdrant_client()
        collections = client.get_collections().collections
        status_info["qdrant"] = {
            "connected": True,
            "collections": [c.name for c in collections],
        }
    except Exception as exc:
        status_info["qdrant"] = {"connected": False, "error": str(exc)}
        status_info["status"] = "degraded"
    
    return status_info

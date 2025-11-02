"""Router for LangChain service."""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator, Iterable

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from rag_api.services.langchain.agent import agent
from rag_api.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    stream: bool = Field(default=False, description="Stream responses for debugging")
    debug: bool = Field(default=True, description="Include debug information in response")


class QueryResponse(BaseModel):
    answer: str
    debug: dict[str, Any] = Field(default_factory=dict, description="Debug information")
    status: str = Field(default="success", description="Response status")


class DebugInfo(BaseModel):
    """Debug information about the agent execution."""

    tools_used: list[str] = Field(default_factory=list)
    steps_taken: int = 0
    messages_count: int = 0
    model_provider: str = ""
    total_tokens: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0


def _extract_tools_from_messages(messages: Iterable[Any]) -> list[str]:
    """Extract tool names used from agent messages."""
    tools_used = []
    for message in messages:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if hasattr(tool_call, "name"):
                    tools_used.append(tool_call.name)
                elif isinstance(tool_call, dict):
                    tools_used.append(tool_call.get("name", "unknown"))
        content = getattr(message, "content", "")
        if isinstance(content, str) and "tool" in content.lower():
            if "rag_query" in content:
                tools_used.append("rag_query")
            if "web_search" in content or "DuckDuckGo" in content:
                tools_used.append("web_search")
    return list(set(tools_used))


def _content_from_messages(messages: Iterable[Any]) -> str:
    """Extract final answer from agent messages."""
    for message in reversed(list(messages)):
        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip():
            if hasattr(message, "type") and message.type == "ai":
                return content
            elif not hasattr(message, "tool_calls") or not message.tool_calls:
                return content
        if isinstance(content, list):
            text_parts = [
                part.get("text", "") for part in content if isinstance(part, dict)
            ]
            joined = " ".join(part for part in text_parts if part)
            if joined:
                return joined
    return ""


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """Query the RAG agent with optional debug information."""
    import time

    settings = get_settings()
    start_time = time.time()

    try:
        logger.info(f"📥 Received query: {request.question[:100]}...")
        logger.debug(f"Query details: debug={request.debug}, full_question={request.question}")
        
        logger.info("🔍 Invoking agent...")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": request.question}]}
        )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        logger.info(f"✅ Agent response received in {execution_time:.2f}ms")
        
    except httpx.ConnectError as exc:
        error_msg = f"Unable to reach model service at {settings.openai_base_url}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=502, detail=error_msg) from exc
    except Exception as exc:
        logger.error(f"Error processing query: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(exc)}") from exc

    # Extract answer
    if isinstance(response, dict) and "messages" in response:
        messages = response["messages"]
        logger.debug(f"📨 Extracted {len(messages)} messages from agent response")
        answer = _content_from_messages(messages)
        logger.debug(f"💬 Answer extracted: {answer[:100]}...")
        
        # Extract debug info if requested
        debug_info = {}
        if request.debug:
            tools_used = _extract_tools_from_messages(messages)
            logger.debug(f"🔧 Tools used: {tools_used}")
            debug_info = {
                "tools_used": tools_used,
                "steps_taken": len(messages),
                "messages_count": len(messages),
                "model_provider": settings.llm_provider,
                "execution_time_ms": round(execution_time, 2),
                "response_structure": "messages" if isinstance(response, dict) else "direct",
            }
            
            # Try to extract token usage if available
            if isinstance(response, dict):
                if "usage_metadata" in response:
                    debug_info["total_tokens"] = response["usage_metadata"]
                elif "tokens" in response:
                    debug_info["total_tokens"] = response["tokens"]
    else:
        answer = getattr(response, "content", str(response))
        debug_info = {
            "model_provider": settings.llm_provider,
            "execution_time_ms": round(execution_time, 2),
            "response_structure": "direct",
        } if request.debug else {}

    logger.info(f"Query processed successfully in {execution_time:.2f}ms")

    return QueryResponse(answer=answer, debug=debug_info, status="success")


@router.post("/query/stream")
async def query_stream(request: QueryRequest) -> StreamingResponse:
    """Stream query responses for real-time debugging."""
    import json
    import time

    settings = get_settings()
    start_time = time.time()

    async def generate_stream() -> AsyncIterator[str]:
        try:
            logger.info(f"Streaming query: {request.question[:100]}...")
            
            # Use astream for streaming responses
            async for chunk in agent.astream(
                {"messages": [{"role": "user", "content": request.question}]}
            ):
                chunk_data = {
                    "type": "chunk",
                    "data": str(chunk),
                    "timestamp": time.time() - start_time,
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
            
            # Send final summary
            execution_time = (time.time() - start_time) * 1000
            summary = {
                "type": "done",
                "execution_time_ms": round(execution_time, 2),
                "model_provider": settings.llm_provider,
            }
            yield f"data: {json.dumps(summary)}\n\n"
            
        except Exception as exc:
            error_data = {
                "type": "error",
                "error": str(exc),
            }
            logger.error(f"Streaming error: {exc}", exc_info=True)
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@router.get("/debug")
async def debug() -> dict[str, Any]:
    """Get detailed debug information for troubleshooting."""
    import logging
    from rag_api.clients.qdrant import get_qdrant_client
    from rag_api.clients.openai import get_openai_client
    
    logger = logging.getLogger(__name__)
    settings = get_settings()
    debug_info = {
        "service": "langchain-rag-api",
        "status": "healthy",
        "configuration": {
            "llm_provider": settings.llm_provider,
            "embedding_provider": settings.embedding_provider,
            "qdrant_url": settings.qdrant_url,
            "collection": settings.qdrant_collection,
        },
    }
    
    # Test Qdrant connection
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        debug_info["qdrant"] = {
            "connected": True,
            "collections": collection_names,
            "collection_exists": settings.qdrant_collection in collection_names,
        }
        
        # Check collection info if it exists
        if settings.qdrant_collection in collection_names:
            info = client.get_collection(settings.qdrant_collection)
            debug_info["qdrant"]["collection_info"] = {
                "points_count": info.points_count,
                "vectors_count": info.vectors_count if hasattr(info, 'vectors_count') else 0,
            }
        else:
            debug_info["qdrant"]["collection_info"] = {
                "error": "Collection does not exist - run ingestion first!",
                "points_count": 0,
            }
    except Exception as exc:
        logger.exception("Failed to connect to Qdrant")
        debug_info["qdrant"] = {
            "connected": False,
            "error": str(exc),
            "collections": [],
        }
        debug_info["status"] = "degraded"
    
    # Test OpenAI client (LLM)
    try:
        openai_client = get_openai_client()
        # Try to list models to verify connection
        debug_info["llm"] = {
            "provider": settings.llm_provider,
            "model": settings.openai_model,
            "base_url": settings.openai_base_url or "default",
            "auth_configured": bool(settings.openai_auth_username and settings.openai_auth_password),
        }
    except Exception as exc:
        logger.exception("Failed to configure LLM client")
        debug_info["llm"] = {
            "error": str(exc),
            "provider": settings.llm_provider,
        }
        debug_info["status"] = "degraded"
    
    # Test Embeddings
    try:
        from rag_api.clients.embeddings import get_embeddings
        embeddings = get_embeddings()
        test_embedding = embeddings.embed_query("test")
        debug_info["embeddings"] = {
            "provider": settings.embedding_provider,
            "model": settings.openai_embedding_model if settings.embedding_provider == "openai" else settings.huggingface_model,
            "dimension": len(test_embedding),
            "working": True,
        }
    except Exception as exc:
        logger.exception("Failed to test embeddings")
        debug_info["embeddings"] = {
            "error": str(exc),
            "working": False,
        }
        debug_info["status"] = "degraded"
    
    return debug_info


@router.get("/status")
async def status() -> dict[str, Any]:
    """Get service status and configuration."""
    settings = get_settings()
    
    # Check connections
    status_info = {
        "service": "langchain-rag-api",
        "status": "healthy",
        "configuration": {
            "llm_provider": settings.llm_provider,
            "embedding_provider": settings.embedding_provider,
            "qdrant_url": settings.qdrant_url,
            "collection": settings.qdrant_collection,
        },
        "langsmith": {
            "tracing_enabled": settings.langsmith_tracing,
            "project": settings.langsmith_project or "rag-api-langchain",
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

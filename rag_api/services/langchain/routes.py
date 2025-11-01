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
        # Check for tool calls in LangGraph agent messages
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if hasattr(tool_call, "name"):
                    tools_used.append(tool_call.name)
                elif isinstance(tool_call, dict):
                    tools_used.append(tool_call.get("name", "unknown"))
        # Also check message content for tool usage patterns
        content = getattr(message, "content", "")
        if isinstance(content, str) and "tool" in content.lower():
            # Try to extract tool name from content
            if "rag_query" in content:
                tools_used.append("rag_query")
            if "web_search" in content or "DuckDuckGo" in content:
                tools_used.append("web_search")
    return list(set(tools_used))  # Remove duplicates


def _content_from_messages(messages: Iterable[Any]) -> str:
    """Extract final answer from agent messages."""
    for message in reversed(list(messages)):
        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip():
            # Skip tool call messages, get final answer
            if hasattr(message, "type") and message.type == "ai":
                return content
            elif not hasattr(message, "tool_calls") or not message.tool_calls:
                return content
        if isinstance(content, list):  # structured content from some models
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
        logger.info(f"Processing query: {request.question[:100]}...")
        
        response = agent.invoke(
            {"messages": [{"role": "user", "content": request.question}]}
        )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
    except httpx.ConnectError as exc:
        error_msg = f"Unable to reach model service"
        if settings.llm_provider == "ollama":
            error_msg += f" at {settings.ollama_base_url}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=502, detail=error_msg) from exc
    except Exception as exc:
        logger.error(f"Error processing query: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(exc)}") from exc

    # Extract answer
    if isinstance(response, dict) and "messages" in response:
        messages = response["messages"]
        answer = _content_from_messages(messages)
        
        # Extract debug info if requested
        debug_info = {}
        if request.debug:
            tools_used = _extract_tools_from_messages(messages)
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

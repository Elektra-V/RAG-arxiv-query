"""Router for LangChain service."""

from __future__ import annotations

import logging
import traceback
from typing import Any, AsyncIterator, Iterable

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from rag_api.services.langchain.agent import agent
from rag_api.settings import get_settings

# Configure detailed logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure debug level is set

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
    """Extract tool names used from agent messages.
    
    Handles multiple message formats:
    - LangChain message objects with tool_calls attribute
    - Dict messages with tool_calls key
    - Tool message types
    - Content-based detection as fallback
    """
    tools_used = []
    for message in messages:
        # Check for tool_calls attribute (LangChain message objects)
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if hasattr(tool_call, "name"):
                    tools_used.append(tool_call.name)
                elif isinstance(tool_call, dict):
                    tools_used.append(tool_call.get("name", "unknown"))
        
        # Check for tool_calls in dict format
        if isinstance(message, dict):
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get("name") or tool_call.get("function", {}).get("name")
                        if tool_name:
                            tools_used.append(tool_name)
                    elif hasattr(tool_call, "name"):
                        tools_used.append(tool_call.name)
            
            # Check for tool message type
            if message.get("type") == "tool":
                tool_name = message.get("name")
                if tool_name:
                    tools_used.append(tool_name)
        
        # Check message type attribute
        if hasattr(message, "type") and message.type == "tool":
            if hasattr(message, "name"):
                tools_used.append(message.name)
        
        # Fallback: content-based detection
        content = getattr(message, "content", message.get("content", "") if isinstance(message, dict) else "")
        if isinstance(content, str) and content.strip():
            if "rag_query" in content:
                tools_used.append("rag_query")
            if "arxiv_search" in content or "ARXIV" in content or "arxiv.org" in content.lower():
                tools_used.append("arxiv_search")
    
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

def _rag_empty_in_messages(messages: Iterable[Any]) -> bool:
    """Detect if RAG query returned empty signal in the conversation."""
    for message in messages:
        content = getattr(message, "content", None)
        if content and isinstance(content, str) and "RAG_EMPTY" in content:
            return True
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and "text" in part and isinstance(part["text"], str):
                    if "RAG_EMPTY" in part["text"]:
                        return True
    return False

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
        error_msg = "Unable to reach model service"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=502, detail=error_msg) from exc
    except ValueError as exc:
        # Configuration errors (missing API key, etc.)
        error_msg = str(exc)
        logger.error(f"Configuration error: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Configuration error: {error_msg}\n\nPlease check your .env file and ensure OPENAI_API_KEY is set correctly."
        ) from exc
    except Exception as exc:
        # Log full traceback for debugging
        error_type = type(exc).__name__
        error_str = str(exc)
        full_traceback = traceback.format_exc()
        
        # Log detailed error information
        logger.error("=" * 80)
        logger.error(f"ERROR TYPE: {error_type}")
        logger.error(f"ERROR MESSAGE: {error_str}")
        logger.error(f"FULL TRACEBACK:\n{full_traceback}")
        logger.error("=" * 80)
        
        # Check for OpenAI authentication errors
        if "AuthenticationError" in error_type or "401" in error_str or "Unauthorized" in error_str:
            logger.error(f"OpenAI authentication failed: {exc}", exc_info=True)
            raise HTTPException(
                status_code=401,
                detail=(
                    "OpenAI API authentication failed. This usually means:\n"
                    "1. OPENAI_API_KEY is not set in .env file, or\n"
                    "2. OPENAI_API_KEY is invalid/expired, or\n"
                    "3. OPENAI_API_KEY has no credits/usage remaining\n\n"
                    "Please check your .env file and verify your API key at https://platform.openai.com/api-keys"
                )
        ) from exc
        
        # Check for InternalServerError (502) from OpenRouter - model unavailable
        if "InternalServerError" in error_type or "502" in error_str:
            logger.error(f"Model service error (502): {exc}", exc_info=True)
            settings = get_settings()
            model_name = settings.openai_model if hasattr(settings, 'openai_model') else "unknown"
            base_url = settings.openai_base_url if hasattr(settings, 'openai_base_url') else None
            
            if base_url and "openrouter" in base_url.lower():
                detail_msg = (
                    f"Model '{model_name}' is currently unavailable on OpenRouter.\n\n"
                    "This usually means:\n"
                    "1. The model provider has no infrastructure available (temporary outage)\n"
                    "2. The model is overloaded or rate-limited\n"
                    "3. The free tier model may have usage limits\n\n"
                    "Solutions:\n"
                    "1. Try a different model (e.g., 'openai/gpt-4o-mini', 'anthropic/claude-3-haiku')\n"
                    "2. Wait a few minutes and try again\n"
                    "3. Check model availability at https://openrouter.ai/models\n"
                    f"4. Update OPENAI_MODEL in your .env file to a different model"
                )
            else:
                detail_msg = (
                    f"Model service error (502): {str(exc)}\n\n"
                    "The model service returned a 502 Bad Gateway error. "
                    "This usually indicates a temporary service outage."
                )
            
            raise HTTPException(status_code=502, detail=detail_msg) from exc

        logger.error(f"Error processing query: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(exc)}") from exc

    # Extract answer
    if isinstance(response, dict) and "messages" in response:
        messages = response["messages"]
        logger.debug(f"📨 Extracted {len(messages)} messages from agent response")
        
        # Extract tools used - always check for validation
        tools_used = _extract_tools_from_messages(messages)
        logger.debug(f"🔧 Tools used: {tools_used}")
        
        # Validate that tools were used
        if not tools_used:
            error_msg = (
                "Agent must use tools (rag_query or arxiv_search) to answer queries. "
                "Direct LLM responses without tools are not allowed."
            )
            logger.warning(f"❌ Validation failed: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        # Enforce: If rag_query yielded no results, arxiv_search must be used
        rag_empty = _rag_empty_in_messages(messages)
        if rag_empty and "rag_query" in tools_used and "arxiv_search" not in tools_used:
            error_msg = (
                "rag_query returned no results (RAG_EMPTY). The agent must call arxiv_search next. "
                "Please retry; direct answers after empty RAG are not allowed."
            )
            logger.warning(f"❌ Validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        answer = _content_from_messages(messages)
        logger.debug(f"💬 Answer extracted: {answer[:100]}...")
        
        # Extract debug info if requested
        debug_info = {}
        if request.debug:
            debug_info = {
                "tools_used": tools_used,
                "tools_required": True,
                "tools_validation_passed": True,
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
        # Direct response without messages structure - this should not happen with ReAct agent
        # but if it does, we still need to validate
        answer = getattr(response, "content", str(response))
        tools_used = []
        logger.warning("⚠️ Received direct response without messages structure")
        
        # Reject direct responses
        error_msg = (
            "Agent must use tools (rag_query or arxiv_search) to answer queries. "
            "Direct LLM responses without tools are not allowed."
        )
        logger.warning(f"❌ Validation failed: {error_msg}")
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )

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
            
            # Collect all messages to validate tool usage at the end
            all_messages = []
            final_response = None
            
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
                
                # Collect messages from chunk for validation
                if isinstance(chunk, dict):
                    if "messages" in chunk:
                        all_messages.extend(chunk["messages"])
                    # Keep track of final response structure
                    if "messages" in chunk or "agent" in chunk:
                        final_response = chunk
            
            # Validate tool usage after streaming completes
            execution_time = (time.time() - start_time) * 1000
            
            # Extract tools used from collected messages
            tools_used = _extract_tools_from_messages(all_messages) if all_messages else []
            
            # Check if tools were used
            if not tools_used:
                error_data = {
                    "type": "error",
                    "error": "Agent must use tools (rag_query or arxiv_search) to answer queries. Direct LLM responses without tools are not allowed.",
                    "validation_failed": True,
                    "execution_time_ms": round(execution_time, 2),
                }
                logger.warning("❌ Streaming validation failed: No tools used")
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            # Enforce arxiv_search after empty RAG
            rag_empty = _rag_empty_in_messages(all_messages or [])
            if rag_empty and "rag_query" in tools_used and "arxiv_search" not in tools_used:
                error_data = {
                    "type": "error",
                    "error": "rag_query returned RAG_EMPTY; agent must call arxiv_search before answering.",
                    "validation_failed": True,
                    "execution_time_ms": round(execution_time, 2),
                }
                logger.warning("❌ Streaming validation failed: RAG_EMPTY without arxiv_search")
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            # Send final summary with validation status
            summary = {
                "type": "done",
                "execution_time_ms": round(execution_time, 2),
                "model_provider": settings.llm_provider,
                "tools_used": tools_used,
                "tools_required": True,
                "tools_validation_passed": True,
            }
            yield f"data: {json.dumps(summary)}\n\n"
            
        except ValueError as exc:
            # Configuration errors
            error_data = {
                "type": "error",
                "error": str(exc),
                "hint": "Please check your .env file and ensure OPENAI_API_KEY is set correctly.",
            }
            logger.error(f"Configuration error: {exc}", exc_info=True)
            yield f"data: {json.dumps(error_data)}\n\n"
        except Exception as exc:
            # Check for OpenAI authentication errors
            error_type = type(exc).__name__
            error_str = str(exc)
            is_auth_error = "AuthenticationError" in error_type or "401" in error_str or "Unauthorized" in error_str
            is_502_error = "InternalServerError" in error_type or "502" in error_str
            
            error_data = {
                "type": "error",
                "error": str(exc),
            }
            
            if is_auth_error:
                error_data["hint"] = (
                    "OpenAI API authentication failed. Check OPENAI_API_KEY in .env file "
                    "or verify at https://platform.openai.com/api-keys"
                )
            elif is_502_error:
                settings = get_settings()
                model_name = settings.openai_model if hasattr(settings, 'openai_model') else "unknown"
                base_url = settings.openai_base_url if hasattr(settings, 'openai_base_url') else None
                
                if base_url and "openrouter" in base_url.lower():
                    error_data["hint"] = (
                        f"Model '{model_name}' is unavailable on OpenRouter. "
                        "Try a different model or check https://openrouter.ai/models for availability."
                    )
                else:
                    error_data["hint"] = "Model service error (502). The service may be temporarily unavailable."
            
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
            "api_key_configured": bool(settings.openai_api_key),
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

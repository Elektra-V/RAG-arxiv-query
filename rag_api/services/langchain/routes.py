"""Router for LangChain service."""

from __future__ import annotations

from typing import Any, Iterable

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from rag_api.services.langchain.agent import agent
from rag_api.settings import get_settings


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


router = APIRouter(prefix="", tags=["query"])


def _content_from_messages(messages: Iterable[Any]) -> str:
    for message in reversed(list(messages)):
        content = getattr(message, "content", None)
        if isinstance(content, str):
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
    settings = get_settings()

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": request.question}]}
        )
    except httpx.ConnectError as exc:  # pragma: no cover - network failure path
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to reach Ollama at "
                f"{settings.ollama_base_url}. Set OLLAMA_BASE_URL to a reachable host."
            ),
        ) from exc

    if isinstance(response, dict) and "messages" in response:
        answer = _content_from_messages(response["messages"])
    else:
        answer = getattr(response, "content", str(response))

    return QueryResponse(answer=answer)

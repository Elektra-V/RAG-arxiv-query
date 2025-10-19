"""Router for LlamaIndex service."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from rag_api.services.llamaindex.index import get_index


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


router = APIRouter(prefix="", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    index = get_index()
    query_engine = index.as_query_engine(
        similarity_top_k=3,
        response_mode="compact",
        summary_mode="tree_summarize",
    )
    response = query_engine.query(request.question)
    return QueryResponse(answer=str(response))

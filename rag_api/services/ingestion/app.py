"""FastAPI application exposing ingestion endpoints."""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag_api.ingestion.pipeline import run_ingestion
from rag_api.logging import configure_logging
from rag_api.settings import get_settings


class IngestionRequest(BaseModel):
    query: str | None = Field(default=None, description="arXiv search query")
    max_docs: int | None = Field(default=None, ge=0, le=25)


class IngestionResponse(BaseModel):
    ingested: int
    query: str


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    api = FastAPI(title="RAG Ingestion Service")

    @api.post("/ingest", response_model=IngestionResponse)
    async def ingest(payload: IngestionRequest) -> IngestionResponse:
        query = payload.query or settings.arxiv_query
        max_docs = payload.max_docs or settings.arxiv_max_docs

        try:
            summary = run_ingestion(query=query, max_docs=max_docs)
        except (
            Exception
        ) as exc:  # pragma: no cover - network failures handled at runtime
            logging.exception("Ingestion failed: %s", exc)
            raise HTTPException(status_code=500, detail="Ingestion failed") from exc

        return IngestionResponse(**summary)

    return api


app = create_app()


def main() -> None:
    settings = get_settings()
    import uvicorn

    uvicorn.run(
        "rag_api.services.ingestion.app:app",
        host=settings.ingestion_host,
        port=settings.ingestion_port,
        reload=False,
    )


if __name__ == "__main__":
    main()

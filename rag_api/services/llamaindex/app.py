"""FastAPI application exposing LlamaIndex retrieval."""

from __future__ import annotations

from fastapi import FastAPI

from rag_api.logging import configure_logging
from rag_api.services.llamaindex.routes import router
from rag_api.settings import get_settings


def create_app() -> FastAPI:
    """Create the FastAPI app."""

    configure_logging()
    api = FastAPI(title="RAG LlamaIndex Service")
    api.include_router(router)

    return api


app = create_app()


def main() -> None:
    """Run the FastAPI server."""

    settings = get_settings()
    import uvicorn

    uvicorn.run(
        "rag_api.services.llamaindex.app:app",
        host=settings.llamaindex_host,
        port=settings.llamaindex_port,
        reload=False,
    )


if __name__ == "__main__":
    main()

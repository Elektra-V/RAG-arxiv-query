"""FastAPI application for LangChain agent service."""

from __future__ import annotations

from fastapi import FastAPI

from rag_api.logging import configure_logging
from rag_api.services.langchain.routes import router
from rag_api.settings import get_settings


def create_app() -> FastAPI:
    """Create the FastAPI app."""

    configure_logging()
    api = FastAPI(
        title="RAG LangChain Service",
        description="RAG API with LangChain agent, LangSmith tracing, and enhanced debugging",
        version="0.1.0",
    )
    api.include_router(router)

    return api


app = create_app()


def main() -> None:
    """Run the FastAPI server."""

    settings = get_settings()
    import uvicorn

    uvicorn.run(
        "rag_api.services.langchain.app:app",
        host=settings.langchain_host,
        port=settings.langchain_port,
        reload=False,
    )


if __name__ == "__main__":
    main()

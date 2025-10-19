"""Command-line interface for ingestion workflow."""

from __future__ import annotations

import logging

import typer

from rag_api.ingestion.arxiv import load_documents
from rag_api.ingestion.store import ensure_collection, upsert_documents
from rag_api.logging import configure_logging
from rag_api.settings import get_settings

app = typer.Typer(help="Ingest arXiv documents into Qdrant.")


@app.command()
def run(query: str | None = None, max_docs: int | None = None) -> None:
    """Run the ingestion pipeline for a query."""

    settings = get_settings()
    logger = configure_logging()

    effective_query = query or settings.arxiv_query
    effective_max_docs = max_docs or settings.arxiv_max_docs

    logger.info(
        "Starting ingestion for query '%s' (max_docs=%s)",
        effective_query,
        effective_max_docs,
    )

    ensure_collection()

    try:
        documents = load_documents(effective_query, effective_max_docs)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to load documents: %s", exc)
        raise typer.Exit(code=1) from exc

    if not documents:
        logger.warning("No documents found for query '%s'", effective_query)
        raise typer.Exit(code=0)

    count = upsert_documents(documents)
    logger.info("Ingested %s documents into Qdrant", count)

    logger.info("Ingestion completed successfully")


def main() -> None:
    """Entry point for Typer CLI."""

    configure_logging(level=logging.INFO)
    app()


if __name__ == "__main__":
    main()

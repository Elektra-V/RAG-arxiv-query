"""Shared configuration utilities."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    arxiv_query: str = "quantum computing"
    arxiv_max_docs: int = 5

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "arxiv_papers"

    huggingface_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    ollama_model: str = "llama3.1:8b-instruct-q4_0"
    ollama_base_url: str = "http://ollama:11434"

    langchain_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_tracing: bool = False

    duckduckgo_results: int = 3

    langchain_host: str = "0.0.0.0"
    langchain_port: int = 8009

    llamaindex_host: str = "0.0.0.0"
    llamaindex_port: int = 8080

    ingestion_host: str = "0.0.0.0"
    ingestion_port: int = 8090


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()

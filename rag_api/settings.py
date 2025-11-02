"""Shared configuration utilities."""

from functools import lru_cache
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    arxiv_query: str = "quantum computing"
    arxiv_max_docs: int = 5

    # Qdrant URL - defaults to localhost for portability
    # Docker Compose will override this via environment variable
    qdrant_url: str = "http://localhost:6334"
    qdrant_collection: str = "arxiv_papers"

    # Model provider - company API gateway (OpenAI-compatible)
    llm_provider: Literal["openai"] = "openai"
    embedding_provider: Literal["huggingface", "openai"] = "openai"  # Default: Uses gateway (fast, no CUDA issues)

    # OpenAI configuration - Gateway mode (primary, recommended)
    # Gateway mode uses Basic auth for free models like Qwen with tooling support
    openai_base_url: Optional[str] = None  # Gateway URL: https://genai.iais.fraunhofer.de/api/v2
    openai_auth_username: Optional[str] = None  # Gateway Basic auth username (required for gateway mode)
    openai_auth_password: Optional[str] = None  # Gateway Basic auth password (required for gateway mode)
    openai_model: str = "Qwen2.5-7B-Instruct"  # Default: Free Qwen model with full tooling/function calling support
    openai_embedding_model: str = "text-embedding-3-small"  # Embedding model from gateway
    
    # OpenAI Platform mode (fallback only - paid, when Basic auth not provided)
    openai_api_key: Optional[str] = None  # Optional: Only needed for OpenAI Platform direct access (paid)
    
    # Company API per-request headers (optional)
    # Format: "Header-Name:value" separated by commas
    # Example: "X-Request-ID:default-id"
    company_api_extra_headers: Optional[str] = None

    # HuggingFace configuration (optional fallback for local embeddings)
    huggingface_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LangChain/LangSmith configuration
    langchain_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_tracing: bool = True  # Enable by default for better debugging
    langsmith_project: Optional[str] = None
    langsmith_endpoint: Optional[str] = None

    duckduckgo_results: int = 3

    langchain_host: str = "0.0.0.0"
    langchain_port: int = 9010  # Changed from 8009 to avoid conflicts

    llamaindex_host: str = "0.0.0.0"
    llamaindex_port: int = 9020  # Changed from 8080 to avoid conflicts

    ingestion_host: str = "0.0.0.0"
    ingestion_port: int = 9030  # Changed from 8090 to avoid conflicts


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()

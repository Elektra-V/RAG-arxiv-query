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

    # Model provider selection: "ollama", "openai", "anthropic", etc.
    llm_provider: Literal["ollama", "openai", "anthropic"] = "ollama"
    embedding_provider: Literal["huggingface", "openai"] = "huggingface"

    # OpenAI configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_base_url: Optional[str] = None  # Custom base URL for company APIs
    openai_auth_username: Optional[str] = None  # Basic auth username
    openai_auth_password: Optional[str] = None  # Basic auth password
    
    # Company API per-request headers (optional)
    # Format: "Header-Name:value" separated by commas
    # These are passed as extra_headers in API calls if needed
    # Example: "X-Request-ID:default-id" (matches company API pattern)
    company_api_extra_headers: Optional[str] = None

    # Anthropic configuration
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # HuggingFace configuration (for local embeddings)
    huggingface_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Ollama configuration (for local LLM)
    # Defaults to localhost for portability
    # Docker Compose will override this via environment variable
    ollama_model: str = "llama3.1:8b-instruct-q4_0"
    ollama_base_url: str = "http://localhost:11434"

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

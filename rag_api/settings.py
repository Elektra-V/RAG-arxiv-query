"""Shared configuration utilities."""

from functools import lru_cache
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ArXiv query settings
    arxiv_query: str = "quantum computing"
    arxiv_max_docs: int = 5

    # Qdrant configuration
    qdrant_url: str = "http://localhost:6334"
    qdrant_collection: str = "arxiv_papers"

    # Model providers
    llm_provider: Literal["openai"] = "openai"
    embedding_provider: Literal["huggingface", "openai"] = "openai"

    # OpenAI Platform configuration (required)
    openai_api_key: Optional[str] = None  # Required: OpenAI Platform API key
    openai_model: str = "gpt-4o-mini"  # Default: OpenAI model
    openai_embedding_model: Optional[str] = None  # Auto-detects based on LLM model if not set
    openai_base_url: Optional[str] = None  # Optional: Custom base URL for gateway/proxy (e.g., OpenRouter, Together AI)
    openrouter_http_referer: Optional[str] = None  # Optional: HTTP-Referer header for OpenRouter
    openrouter_x_title: Optional[str] = None  # Optional: X-Title header for OpenRouter

    # HuggingFace configuration (optional fallback for local embeddings)
    huggingface_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LangChain/LangSmith configuration
    langchain_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_tracing: bool = True
    langsmith_project: Optional[str] = None
    langsmith_endpoint: Optional[str] = None

    # Search configuration
    arxiv_search_max_results: int = 5
    rag_chunk_max_length: int = 1000  # Max characters per RAG chunk to prevent context overflow
    arxiv_summary_max_length: int = 400  # Max characters per arXiv summary

    # Service ports
    langchain_host: str = "0.0.0.0"
    langchain_port: int = 9010

    llamaindex_host: str = "0.0.0.0"
    llamaindex_port: int = 9020

    ingestion_host: str = "0.0.0.0"
    ingestion_port: int = 9030

    # APO (Automatic Prompt Optimization) settings
    apo_optimized_prompt_path: Optional[str] = None  # Path to optimized prompt file (default: "optimized_prompt.txt")
    apo_use_optimized_prompt: bool = True  # If false, always use baseline prompt


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Note: Settings are cached for performance. If you change .env file,
    restart the application or clear the cache for changes to take effect.
    """
    return Settings()


def clear_settings_cache() -> None:
    """Clear the settings cache to force reload from .env file.
    
    Use this if you've updated .env file and want to reload settings
    without restarting the application.
    """
    get_settings.cache_clear()

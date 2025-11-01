"""Embedding utilities."""

from functools import lru_cache

from langchain_core.embeddings import Embeddings

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None

from rag_api.settings import get_settings


@lru_cache
def get_embeddings() -> Embeddings:
    """Return a cached embedding model instance based on provider settings."""

    settings = get_settings()

    if settings.embedding_provider == "openai":
        if OpenAIEmbeddings is None:
            raise ImportError(
                "langchain-openai is not installed. Install it with: uv add langchain-openai"
            )
        # API key can be provided via env var OPENAI_API_KEY or explicitly
        api_key = settings.openai_api_key  # None if not set, SDK will use OPENAI_API_KEY env var
        # Note: If no API key is provided, the SDK will try to read from OPENAI_API_KEY env var
        # If that also fails, it will raise an error when first used - which is fine for now
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=api_key,
        )

    elif settings.embedding_provider == "huggingface":
        if HuggingFaceEmbeddings is None:
            raise ImportError(
                "langchain-huggingface is not installed. Install it with: uv add langchain-huggingface"
            )
        return HuggingFaceEmbeddings(model_name=settings.huggingface_model)

    else:
        raise ValueError(
            f"Unsupported embedding provider: {settings.embedding_provider}. "
            "Supported providers: 'huggingface', 'openai'"
        )

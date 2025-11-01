"""LangChain agent wiring."""

from __future__ import annotations

import os

from langchain_core.language_models import BaseChatModel

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None

from langgraph.prebuilt import create_react_agent

from rag_api.clients.openai import get_openai_client
from rag_api.services.langchain.tools import get_tools
from rag_api.settings import get_settings


def configure_langsmith() -> None:
    """Configure LangSmith tracing for debugging and observability.
    
    Gracefully handles missing API keys by disabling tracing if no key is available.
    """
    settings = get_settings()
    
    if settings.langsmith_tracing:
        # Set LangSmith environment variables
        if settings.langsmith_api_key:
            os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
        else:
            # If no API key but tracing enabled, check if it's in env
            if os.getenv("LANGCHAIN_API_KEY"):
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
            else:
                # Disable if no API key available - don't crash, just disable tracing
                os.environ["LANGCHAIN_TRACING_V2"] = "false"
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    "LangSmith tracing is enabled but no API key found. "
                    "Set LANGSMITH_API_KEY or LANGCHAIN_API_KEY to enable tracing. "
                    "Tracing is now disabled."
                )
                return
        
        if settings.langsmith_project:
            os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        else:
            os.environ["LANGCHAIN_PROJECT"] = "rag-api-langchain"
        
        if settings.langsmith_endpoint:
            os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint


def get_llm_model() -> BaseChatModel:
    """Get the configured LLM model based on provider settings."""
    settings = get_settings()

    if settings.llm_provider == "openai":
        if ChatOpenAI is None:
            raise ImportError(
                "langchain-openai is not installed. Install it with: uv add langchain-openai"
            )
        
        # Use the centralized OpenAI client factory
        # This handles Basic auth encoding and client creation according to company API pattern
        openai_client = get_openai_client()
        
        # Create LangChain ChatOpenAI wrapper with the configured client
        return ChatOpenAI(
            model=settings.openai_model,
            client=openai_client,
            temperature=0,
        )

    elif settings.llm_provider == "anthropic":
        if ChatAnthropic is None:
            raise ImportError(
                "langchain-anthropic is not installed. Install it with: uv add langchain-anthropic"
            )
        # API key can be provided via env var ANTHROPIC_API_KEY or explicitly
        api_key = settings.anthropic_api_key  # None if not set, SDK will use ANTHROPIC_API_KEY env var
        return ChatAnthropic(
            model=settings.anthropic_model,
            api_key=api_key,
            temperature=0,
        )

    elif settings.llm_provider == "ollama":
        if ChatOllama is None:
            raise ImportError(
                "langchain-ollama is not installed. Install it with: uv add langchain-ollama"
            )
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {settings.llm_provider}. "
            "Supported providers: 'ollama', 'openai', 'anthropic'"
        )


def build_agent():
    """Construct the ReAct agent with configured tools."""

    # Configure LangSmith before building agent
    configure_langsmith()
    
    model = get_llm_model()
    tools = get_tools()
    prompt = (
        "You are a helpful assistant for academic queries. "
        "Prefer using rag_query when the answer likely exists in the arXiv collection. "
        "If rag_query returns no results or insufficient context, immediately switch to web_search. "
        "Use web_search for recent information or when the knowledge base lacks coverage."
    )
    return create_react_agent(model=model, tools=tools, prompt=prompt)


agent = build_agent()

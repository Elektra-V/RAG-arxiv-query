"""LangChain agent wiring."""

from __future__ import annotations

import os

from langchain_core.language_models import BaseChatModel

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

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
    """Get the configured LLM model for OpenAI Platform."""
    settings = get_settings()

    if ChatOpenAI is None:
        raise ImportError(
            "langchain-openai is not installed. Install it with: uv add langchain-openai"
        )
    
    openai_client = get_openai_client()
    return ChatOpenAI(
        model=settings.openai_model,
        client=openai_client,
        temperature=0,
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

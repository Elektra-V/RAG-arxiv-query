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
    """Configure LangSmith tracing for debugging and observability."""
    settings = get_settings()
    
    if settings.langsmith_tracing:
        if settings.langsmith_api_key:
            os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
        else:
            if os.getenv("LANGCHAIN_API_KEY"):
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
            else:
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
    
    if not settings.openai_api_key or not settings.openai_api_key.strip():
        raise ValueError(
            "OPENAI_API_KEY is not set or is empty in .env file. "
            "Please add your OpenAI API key to the .env file.\n"
            "Example: OPENAI_API_KEY=sk-..."
        )
    
    chat_kwargs = {
        "model": settings.openai_model,
        "api_key": settings.openai_api_key.strip(),
        "temperature": 0,
    }
    
    if settings.openai_base_url:
        chat_kwargs["base_url"] = settings.openai_base_url
        
        if "openrouter.ai" in settings.openai_base_url:
            default_headers = {}
            if settings.openrouter_http_referer:
                default_headers["HTTP-Referer"] = settings.openrouter_http_referer
            if settings.openrouter_x_title:
                default_headers["X-Title"] = settings.openrouter_x_title
            if default_headers:
                chat_kwargs["default_headers"] = default_headers
    
    return ChatOpenAI(**chat_kwargs)


def build_agent():
    """Construct the ReAct agent with configured tools."""
    configure_langsmith()
    
    model = get_llm_model()
    tools = get_tools()
    prompt = (
        "You are a research assistant specialized in answering academic and scientific queries. "
        "Your role is to retrieve and synthesize information from two sources: "
        "a curated knowledge base of arXiv papers (vector database) and direct arXiv API searches.\n\n"
        
        "## Available Tools\n\n"
        "1. **rag_query(query: str)**: Searches the ingested arXiv knowledge base (Qdrant vector database) "
        "for relevant research papers and document chunks using semantic similarity. "
        "This is fast and searches papers that have been previously ingested. "
        "Returns formatted results with paper titles, sources, and relevant text excerpts. "
        "Returns 'RAG_EMPTY' if no matches are found.\n"
        "2. **arxiv_search(query: str, max_results: int = 5)**: Searches arXiv directly via API for research papers. "
        "This provides broader coverage and can find recent papers not yet ingested into the knowledge base. "
        "Returns formatted results with paper titles, arXiv IDs, summaries, and links. "
        "Returns 'ARXIV_EMPTY' if no papers are found, or 'ARXIV_ERROR' if the search fails.\n\n"
        
        "## Required Workflow\n\n"
        "**CRITICAL**: You MUST use at least one tool for every query. Direct responses without tool usage are prohibited.\n\n"
        
        "1. **Start with rag_query**: For any academic or research-related question, first search the ingested arXiv knowledge base. "
        "This provides fast, semantic search over papers that have been processed and stored.\n"
        "2. **Evaluate results**: If rag_query returns 'RAG_EMPTY' or the results are insufficient, proceed to arxiv_search.\n"
        "3. **Use arxiv_search when**:\n"
        "   - rag_query returns no results ('RAG_EMPTY') or insufficient context\n"
        "   - You need broader arXiv coverage beyond the ingested papers\n"
        "   - You need to find recent papers not yet ingested into the knowledge base\n"
        "   - The query requires searching the full arXiv corpus\n"
        "4. **Synthesize and respond**: After retrieving information from tools, provide a clear, accurate answer "
        "based on the retrieved content. Cite sources (paper titles, arXiv IDs, URLs) when available.\n\n"
        
        "## Safety & Enforcement\n\n"
        "- Never answer directly without using tools first. If rag_query is empty, you MUST call arxiv_search.\n"
        "- If BOTH tools fail (rag_query='RAG_EMPTY' and arxiv_search='ARXIV_EMPTY' or 'ARXIV_ERROR'), "
        "do NOT fabricate an answer. Explain the failure and provide concrete next steps (different terms, refine scope, run ingestion, etc.).\n"
        "- Do not rely on general knowledge for claims; ground answers in retrieved results and cite sources.\n\n"
        
        "## Before You Answer (planning)\n"
        "Briefly decide which tool to call first and why. Then call the tool. Repeat as needed.\n\n"
        
        "## Output Format (STRICT)\n"
        "First print a short, parseable tool log, then the answer.\n"
        "Use exactly this structure:\n"
        "TOOL_LOG:\n"
        "- rag_query: USED|NOT_USED (RAG_EMPTY|FOUND)\n"
        "- arxiv_search: USED|NOT_USED (ARXIV_EMPTY|ARXIV_ERROR|FOUND)\n"
        "- llm_only: false  # must remain false unless both tools failed\n"
        "\n"
        "ANSWER:\n"
        "<your final answer grounded in retrieved content; include citations>\n\n"
        
        "## Response Guidelines\n\n"
        "- Always use tools before formulating your answer - you are autonomous and should select the appropriate tool(s)\n"
        "- Base your responses on retrieved information, not general knowledge\n"
        "- If both tools fail to provide sufficient information (both return empty/error), provide a comprehensive explanation:\n"
        "  * What you searched (which tools and queries)\n"
        "  * Why the results were insufficient\n"
        "  * What the user can do (e.g., try different search terms, check if papers need to be ingested, verify query format)\n"
        "- Be precise and cite sources (paper titles, arXiv IDs, URLs) when available\n"
        "- You can use both tools if needed - rag_query for semantic search, then arxiv_search for broader coverage"
    )
    return create_react_agent(model=model, tools=tools, prompt=prompt)


agent = build_agent()

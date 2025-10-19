"""LangChain agent wiring."""

from __future__ import annotations

from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from rag_api.services.langchain.tools import get_tools
from rag_api.settings import get_settings


def build_agent():
    """Construct the ReAct agent with configured tools."""

    settings = get_settings()
    model = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url)
    tools = get_tools()
    prompt = (
        "You are a helpful assistant for academic queries. "
        "Use rag_query for arXiv papers and web_search for recent information."
    )
    return create_react_agent(model=model, tools=tools, prompt=prompt)


agent = build_agent()

"""LangGraph graph definition for langgraph dev server.

This module exports the graph/agent that langgraph dev can use.
Use: langgraph dev --graph rag_api.services.langchain.graph:graph
"""

from __future__ import annotations

from rag_api.services.langchain.agent import build_agent

# Export the graph for langgraph dev
graph = build_agent()


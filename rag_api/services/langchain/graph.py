"""LangGraph graph definition for langgraph dev server."""

from __future__ import annotations

import logging

from rag_api.services.langchain.agent import build_agent, _load_optimized_prompt

logger = logging.getLogger(__name__)

optimized_prompt = _load_optimized_prompt()

if optimized_prompt:
    from rag_api.services.langchain.prompt_template import get_baseline_prompt_template
    from rag_api.services.langchain.prompt_comparison import show_prompt_comparison
    
    baseline_prompt = get_baseline_prompt_template()
    show_prompt_comparison(baseline_prompt, optimized_prompt)
    graph = build_agent(prompt_template=optimized_prompt)
else:
    logger.info("Using baseline prompt (run train_apo.py to optimize)")
    graph = build_agent()

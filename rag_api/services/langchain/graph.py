"""LangGraph graph definition for langgraph dev server."""

from __future__ import annotations

import logging
from pathlib import Path

from rag_api.services.langchain.agent import build_agent
from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


def _load_optimized_prompt() -> str | None:
    """Load optimized prompt from file if exists."""
    settings = get_settings()
    
    if settings.apo_optimized_prompt_path:
        optimized_path = Path(settings.apo_optimized_prompt_path)
        if optimized_path.exists():
            try:
                return optimized_path.read_text(encoding='utf-8')
            except Exception as e:
                logger.warning(f"Failed to load optimized prompt: {e}")
    
    optimized_path = Path("optimized_prompt.txt")
    if optimized_path.exists():
        try:
            return optimized_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"Failed to load optimized prompt: {e}")
    
    project_root = Path(__file__).parent.parent.parent.parent
    optimized_path = project_root / "optimized_prompt.txt"
    if optimized_path.exists():
        try:
            return optimized_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"Failed to load optimized prompt: {e}")
    
    return None


optimized_prompt = _load_optimized_prompt()

if optimized_prompt:
    from rag_api.services.langchain.prompt_template import get_baseline_prompt_template
    from rag_api.services.langchain.prompt_comparison import show_prompt_comparison
    
    baseline_prompt = get_baseline_prompt_template()
    show_prompt_comparison(baseline_prompt, optimized_prompt)
    graph = build_agent(prompt_template=optimized_prompt)
else:
    logger.info("📝 Using baseline prompt (run train_apo.py to optimize)")
    graph = build_agent()

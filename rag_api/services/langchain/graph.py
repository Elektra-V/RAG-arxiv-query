"""LangGraph graph definition for langgraph dev server.

This module exports the graph/agent that langgraph dev can use.
Use: langgraph dev --graph rag_api.services.langchain.graph:graph

The graph automatically loads optimized prompts if available from APO training.
"""

from __future__ import annotations

import logging
from pathlib import Path

from rag_api.services.langchain.agent import build_agent

logger = logging.getLogger(__name__)


def _load_optimized_prompt() -> str | None:
    """Load optimized prompt from file if it exists.
    
    Checks:
    1. APO_OPTIMIZED_PROMPT_PATH from settings (if set)
    2. optimized_prompt.txt in current directory
    3. optimized_prompt.txt in project root
    
    Returns:
        Optimized prompt string if file exists, None otherwise
    """
    from rag_api.settings import get_settings
    
    settings = get_settings()
    
    # Check custom path from settings first
    if settings.apo_optimized_prompt_path:
        optimized_path = Path(settings.apo_optimized_prompt_path)
        if optimized_path.exists():
            try:
                prompt = optimized_path.read_text(encoding='utf-8')
                logger.info(f"✓ Loaded optimized prompt from {optimized_path}")
                return prompt
            except Exception as e:
                logger.warning(f"Failed to load optimized prompt from {optimized_path}: {e}")
    
    # Check for optimized prompt file in current directory (created by train_apo.py)
    optimized_path = Path("optimized_prompt.txt")
    if optimized_path.exists():
        try:
            prompt = optimized_path.read_text(encoding='utf-8')
            logger.info(f"✓ Loaded optimized prompt from {optimized_path}")
            return prompt
        except Exception as e:
            logger.warning(f"Failed to load optimized prompt: {e}")
    
    # Also check in project root (if running from different directory)
    project_root = Path(__file__).parent.parent.parent.parent
    optimized_path = project_root / "optimized_prompt.txt"
    if optimized_path.exists():
        try:
            prompt = optimized_path.read_text(encoding='utf-8')
            logger.info(f"✓ Loaded optimized prompt from {optimized_path}")
            return prompt
        except Exception as e:
            logger.warning(f"Failed to load optimized prompt: {e}")
    
    return None


# Load optimized prompt if available, otherwise use baseline
optimized_prompt = _load_optimized_prompt()

if optimized_prompt:
    logger.info("🚀 Using OPTIMIZED prompt from APO training")
    graph = build_agent(prompt_template=optimized_prompt)
else:
    logger.info("📝 Using baseline prompt (run train_apo.py to optimize)")
    graph = build_agent()


"""LangChain agent wiring."""

from __future__ import annotations

import os
import logging
from pathlib import Path

from langchain_core.language_models import BaseChatModel

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

from langgraph.prebuilt import create_react_agent

from rag_api.services.langchain.tools import get_tools
from rag_api.settings import get_settings

logger = logging.getLogger(__name__)


def configure_langsmith() -> None:
    """Configure LangSmith tracing."""
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
                logger.warning(
                    "LangSmith tracing is enabled but no API key found. "
                    "Set LANGSMITH_API_KEY or LANGCHAIN_API_KEY to enable tracing."
                )
                return
        
        if settings.langsmith_project:
            os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        else:
            os.environ["LANGCHAIN_PROJECT"] = "rag-api-langchain"
        
        if settings.langsmith_endpoint:
            os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint


def get_llm_model() -> BaseChatModel:
    """Get configured LLM model."""
    settings = get_settings()

    if ChatOpenAI is None:
        raise ImportError("langchain-openai is not installed. Install it with: uv add langchain-openai")
    
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


def build_agent(prompt_template: str | None = None):
    """Construct ReAct agent with configured tools."""
    configure_langsmith()
    
    model = get_llm_model()
    tools = get_tools()
    
    if prompt_template is None:
        from rag_api.services.langchain.prompt_template import get_baseline_prompt_template
        prompt = get_baseline_prompt_template()
    else:
        prompt = prompt_template
    
    return create_react_agent(model=model, tools=tools, prompt=prompt)


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
    agent = build_agent(prompt_template=optimized_prompt)
else:
    logger.info("📝 Using baseline prompt (run train_apo.py to optimize)")
    agent = build_agent()

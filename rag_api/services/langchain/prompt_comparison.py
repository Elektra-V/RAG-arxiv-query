"""Prompt comparison utilities."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def show_prompt_comparison(baseline_prompt: str, optimized_prompt: str) -> None:
    """Display concise prompt comparison."""
    length_diff = len(optimized_prompt) - len(baseline_prompt)
    logger.info(f"✅ Using optimized prompt ({length_diff:+d} chars, {len(optimized_prompt.splitlines())} lines)")

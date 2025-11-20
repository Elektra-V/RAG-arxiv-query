"""Helper functions for displaying prompt comparison."""

from __future__ import annotations

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def show_prompt_comparison(baseline_prompt: str, optimized_prompt: str) -> None:
    """Display a formatted before/after comparison of prompts.
    
    Args:
        baseline_prompt: The original baseline prompt
        optimized_prompt: The optimized prompt from APO training
    """
    logger.info("=" * 80)
    logger.info("🚀 PROMPT OPTIMIZATION COMPARISON")
    logger.info("=" * 80)
    
    # Show baseline prompt (first 500 chars)
    logger.info("\n📝 BASELINE PROMPT (Before Optimization):")
    logger.info("-" * 80)
    baseline_preview = baseline_prompt[:500] + "..." if len(baseline_prompt) > 500 else baseline_prompt
    logger.info(baseline_preview)
    logger.info(f"\n   Length: {len(baseline_prompt)} characters")
    logger.info(f"   Lines: {len(baseline_prompt.splitlines())} lines")
    
    # Show optimized prompt (first 500 chars)
    logger.info("\n✨ OPTIMIZED PROMPT (After Optimization):")
    logger.info("-" * 80)
    optimized_preview = optimized_prompt[:500] + "..." if len(optimized_prompt) > 500 else optimized_prompt
    logger.info(optimized_preview)
    logger.info(f"\n   Length: {len(optimized_prompt)} characters")
    logger.info(f"   Lines: {len(optimized_prompt.splitlines())} lines")
    
    # Calculate differences
    baseline_words = set(word.lower() for word in baseline_prompt.split() if len(word) > 3)
    optimized_words = set(word.lower() for word in optimized_prompt.split() if len(word) > 3)
    new_words = optimized_words - baseline_words
    removed_words = baseline_words - optimized_words
    
    # Show key statistics
    logger.info("\n📊 KEY CHANGES:")
    length_diff = len(optimized_prompt) - len(baseline_prompt)
    logger.info(f"   • Prompt length change: {length_diff:+d} characters ({length_diff/len(baseline_prompt)*100:+.1f}%)")
    
    if new_words:
        sample_new = list(new_words)[:5]
        logger.info(f"   • New keywords added: {len(new_words)} (sample: {', '.join(sample_new)})")
    
    if removed_words:
        sample_removed = list(removed_words)[:5]
        logger.info(f"   • Keywords removed: {len(removed_words)} (sample: {', '.join(sample_removed)})")
    
    # Show similarity percentage
    if baseline_words:
        similarity = len(baseline_words & optimized_words) / len(baseline_words) * 100
        logger.info(f"   • Word overlap: {similarity:.1f}%")
    
    logger.info("=" * 80)
    logger.info("✅ Using OPTIMIZED prompt from APO training")
    logger.info("=" * 80)


def get_prompt_diff(baseline_prompt: str, optimized_prompt: str) -> Tuple[str, str]:
    """Get a simple diff-like comparison of prompts.
    
    Args:
        baseline_prompt: The original baseline prompt
        optimized_prompt: The optimized prompt
        
    Returns:
        Tuple of (added_text, removed_text) summaries
    """
    baseline_lines = baseline_prompt.splitlines()
    optimized_lines = optimized_prompt.splitlines()
    
    # Simple comparison - show first few lines that differ
    added = []
    removed = []
    
    max_lines = min(len(baseline_lines), len(optimized_lines), 10)
    for i in range(max_lines):
        if i < len(optimized_lines) and i < len(baseline_lines):
            if optimized_lines[i] != baseline_lines[i]:
                if len(optimized_lines[i]) > len(baseline_lines[i]):
                    added.append(optimized_lines[i][:100])
                else:
                    removed.append(baseline_lines[i][:100])
    
    added_summary = "\n".join(added[:3]) if added else "No major additions detected"
    removed_summary = "\n".join(removed[:3]) if removed else "No major removals detected"
    
    return added_summary, removed_summary


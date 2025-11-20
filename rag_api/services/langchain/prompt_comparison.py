"""Prompt comparison utilities."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def show_prompt_comparison(baseline_prompt: str, optimized_prompt: str) -> None:
    """Display before/after prompt comparison."""
    logger.info("=" * 80)
    logger.info("🚀 PROMPT OPTIMIZATION COMPARISON")
    logger.info("=" * 80)
    
    baseline_preview = baseline_prompt[:500] + "..." if len(baseline_prompt) > 500 else baseline_prompt
    logger.info("\n📝 BASELINE PROMPT (Before Optimization):")
    logger.info("-" * 80)
    logger.info(baseline_preview)
    logger.info(f"\n   Length: {len(baseline_prompt)} characters")
    logger.info(f"   Lines: {len(baseline_prompt.splitlines())} lines")
    
    optimized_preview = optimized_prompt[:500] + "..." if len(optimized_prompt) > 500 else optimized_prompt
    logger.info("\n✨ OPTIMIZED PROMPT (After Optimization):")
    logger.info("-" * 80)
    logger.info(optimized_preview)
    logger.info(f"\n   Length: {len(optimized_prompt)} characters")
    logger.info(f"   Lines: {len(optimized_prompt.splitlines())} lines")
    
    baseline_words = set(word.lower() for word in baseline_prompt.split() if len(word) > 3)
    optimized_words = set(word.lower() for word in optimized_prompt.split() if len(word) > 3)
    new_words = optimized_words - baseline_words
    removed_words = baseline_words - optimized_words
    
    logger.info("\n📊 KEY CHANGES:")
    length_diff = len(optimized_prompt) - len(baseline_prompt)
    logger.info(f"   • Prompt length change: {length_diff:+d} characters ({length_diff/len(baseline_prompt)*100:+.1f}%)")
    
    if new_words:
        sample_new = list(new_words)[:5]
        logger.info(f"   • New keywords added: {len(new_words)} (sample: {', '.join(sample_new)})")
    
    if removed_words:
        sample_removed = list(removed_words)[:5]
        logger.info(f"   • Keywords removed: {len(removed_words)} (sample: {', '.join(sample_removed)})")
    
    if baseline_words:
        similarity = len(baseline_words & optimized_words) / len(baseline_words) * 100
        logger.info(f"   • Word overlap: {similarity:.1f}%")
    
    logger.info("=" * 80)
    logger.info("✅ Using OPTIMIZED prompt from APO training")
    logger.info("=" * 80)

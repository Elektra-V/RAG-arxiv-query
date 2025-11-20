"""APO training configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class APOConfig:
    """Configuration for Automatic Prompt Optimization."""
    
    num_runners: int = 1
    num_iterations: int = 2
    learning_rate: float = 0.1
    samples_per_iteration: int = 3
    use_validation: bool = False
    random_seed: int = 42


def get_apo_config() -> APOConfig:
    """Return default APO configuration."""
    return APOConfig()

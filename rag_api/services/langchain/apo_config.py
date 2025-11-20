"""Configuration for APO training."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class APOConfig:
    """Configuration for Automatic Prompt Optimization."""
    
    # Number of parallel runners for training
    num_runners: int = 4
    
    # Number of training iterations
    num_iterations: int = 10
    
    # Learning rate for prompt optimization
    learning_rate: float = 0.1
    
    # Number of samples per iteration
    samples_per_iteration: int = 8
    
    # Whether to use validation set for evaluation
    use_validation: bool = True
    
    # Random seed for reproducibility
    random_seed: int = 42


def get_apo_config() -> APOConfig:
    """Get default APO configuration.
    
    Returns:
        APOConfig instance with default settings
    """
    return APOConfig()


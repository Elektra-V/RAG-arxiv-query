"""Configuration for APO training."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class APOConfig:
    """Configuration for Automatic Prompt Optimization.
    
    Minimal cost settings for cost-effective optimization:
    - Reduced iterations and samples for quick testing
    - Can be increased for more thorough optimization if needed
    """
    
    # Number of parallel runners for training
    num_runners: int = 1  # Reduced from 4 to 1 for minimal cost
    
    # Number of training iterations
    num_iterations: int = 2  # Reduced from 10 to 2 for minimal cost
    
    # Learning rate for prompt optimization
    learning_rate: float = 0.1
    
    # Number of samples per iteration
    samples_per_iteration: int = 3  # Reduced from 8 to 3 for minimal cost
    
    # Whether to use validation set for evaluation
    use_validation: bool = False  # Disabled for minimal cost
    
    # Random seed for reproducibility
    random_seed: int = 42


def get_apo_config() -> APOConfig:
    """Get default APO configuration.
    
    Returns:
        APOConfig instance with default settings
    """
    return APOConfig()


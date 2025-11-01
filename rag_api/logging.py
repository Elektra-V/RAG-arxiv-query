"""Logging configuration helpers."""

import logging
import sys
from logging import Logger


def configure_logging(level: int = logging.INFO) -> Logger:
    """Configure root logger with enhanced formatting and return it."""

    # Create a more detailed format for debugging
    log_format = (
        "%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s"
    )
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,  # Override any existing configuration
    )
    
    # Set log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger("rag_api")

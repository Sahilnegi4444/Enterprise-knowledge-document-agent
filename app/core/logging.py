import logging
import sys
from typing import Any

# Define a professional format
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"

def setup_logger(name: str = "enterprise_agent") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
    return logger

logger = setup_logger()

def log_step(step_name: str, status: str, details: str = "") -> None:
    """Helper to log agent execution phases clearly."""
    message = f"[{step_name.upper()}] - {status}"
    if details:
        message += f" | {details}"
    logger.info(message)

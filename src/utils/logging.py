"""Structured logging infrastructure supporting console and JSON formats."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_format: str = "console",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Configure structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Format style ('console' with colorized text or 'json' for machine parsing).
        log_file: Optional path to append log outputs.

    Returns:
        Root logger instance configured for the application.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger("ai_signal")
    logger.setLevel(numeric_level)
    logger.handlers.clear()

    # Formatter configuration
    if log_format.lower() == "json":
        formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s", "level":"%(levelname)s", "module":"%(name)s", "message":"%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)-7s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logging()

"""
utils/logger.py
---------------
Centralised logging configuration for CineMatch backend.

Usage
-----
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Server started")

All modules should call get_logger(__name__) to obtain their own
named logger so log output clearly identifies its source.
"""

import logging
import sys
from config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT


def _configure_root_logger() -> None:
    """
    Configure the root logger once.  Called at module import time.
    Outputs to stdout so logs are visible in the terminal and can be
    captured by process managers (Docker, systemd, etc.).
    """
    root = logging.getLogger()

    # Avoid adding duplicate handlers if this module is imported twice
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    )
    root.addHandler(handler)
    root.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))


# Initialise on import
_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.

    Args:
        name: typically __name__ of the calling module.

    Returns:
        logging.Logger instance.
    """
    return logging.getLogger(name)

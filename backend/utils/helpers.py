"""
utils/helpers.py
----------------
Shared utility functions used across the CineMatch backend.

Includes:
  - JSON response builders
  - Execution timer context manager
  - Movie title → year extractor
"""

import re
import time
from contextlib import contextmanager
from typing import Any, Generator

from flask import jsonify
from utils.logger import get_logger

logger = get_logger(__name__)


# ─── Response Builders ────────────────────────────────────────────────────────

def success_response(data: dict, status_code: int = 200):
    """
    Build a standard JSON success response.

    Args:
        data:        Dict of fields to include in the response body.
        status_code: HTTP status code (default 200).

    Returns:
        Flask (Response, int) tuple.
    """
    return jsonify({"success": True, **data}), status_code


def error_response(message: str, status_code: int = 400):
    """
    Build a standard JSON error response.
    Stack traces are never included — only a user-safe message.

    Args:
        message:     Human-readable error description.
        status_code: HTTP status code (default 400).

    Returns:
        Flask (Response, int) tuple.
    """
    return jsonify({"success": False, "message": message}), status_code


# ─── Execution Timer ──────────────────────────────────────────────────────────

@contextmanager
def timer(label: str) -> Generator[None, None, None]:
    """
    Context manager that logs the wall-clock time of the wrapped block.

    Usage::

        with timer("KNN inference"):
            distances, indices = knn.kneighbors(vec)

    Args:
        label: Human-readable description logged alongside the elapsed time.
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("%s completed in %.1f ms", label, elapsed_ms)


# ─── Movie Metadata Helpers ───────────────────────────────────────────────────

_YEAR_PATTERN = re.compile(r"\((\d{4})\)\s*$")


def extract_year(title: str) -> int | None:
    """
    Extract the release year from a MovieLens-style title string.

    MovieLens titles follow the format: ``Movie Name (YYYY)``

    Examples::

        extract_year("Toy Story (1995)")    → 1995
        extract_year("No year here")        → None

    Args:
        title: Movie title string from the matrix columns or movies.csv.

    Returns:
        Four-digit integer year, or None if not parseable.
    """
    match = _YEAR_PATTERN.search(title.strip())
    if match:
        return int(match.group(1))
    return None


def split_genres(genres_str: str) -> list[str]:
    """
    Split a pipe-separated genres string into a list.

    Examples::

        split_genres("Action|Crime|Drama")  → ["Action", "Crime", "Drama"]
        split_genres("Drama")               → ["Drama"]
        split_genres("")                    → []
        split_genres("(no genres listed)")  → []

    Args:
        genres_str: Raw genres value from movies.csv.

    Returns:
        List of individual genre strings.
    """
    if not genres_str or genres_str.strip() == "(no genres listed)":
        return []
    return [g.strip() for g in genres_str.split("|") if g.strip()]

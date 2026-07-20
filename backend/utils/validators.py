"""
utils/validators.py
-------------------
Request validation for the CineMatch backend.

All validation logic is centralised here so route handlers stay thin
and validation rules can be updated in one place.
"""

from typing import Any
from config import (
    MIN_K,
    MAX_K,
    MIN_RECOMMENDATIONS,
    MAX_RECOMMENDATIONS,
)


# ─── Result type ──────────────────────────────────────────────────────────────

class ValidationResult:
    """
    Lightweight result object returned by every validator.

    Attributes:
        valid:   True when the input passed all checks.
        message: Human-readable error message (empty string when valid).
    """

    def __init__(self, valid: bool, message: str = ""):
        self.valid   = valid
        self.message = message

    def __bool__(self) -> bool:
        return self.valid


# ─── Field-level validators ───────────────────────────────────────────────────

def validate_user_id(value: Any) -> ValidationResult:
    """
    Validate the user_id field from the request body.

    Rules:
      - Must be present (not None).
      - Must be a positive integer.
      - Whether the user exists in the matrix is checked separately
        by the recommendation service (concerns are intentionally separated).

    Args:
        value: Raw value from request JSON (may be any type).

    Returns:
        ValidationResult
    """
    if value is None:
        return ValidationResult(False, "Missing required field: 'user_id'.")
    try:
        uid = int(value)
    except (TypeError, ValueError):
        return ValidationResult(False, f"'user_id' must be an integer, got: {value!r}.")
    if uid <= 0:
        return ValidationResult(False, f"'user_id' must be a positive integer, got: {uid}.")
    return ValidationResult(True)


def validate_k(value: Any) -> ValidationResult:
    """
    Validate the k (number of nearest neighbours) field.

    Rules:
      - Must be present.
      - Must be an integer in [MIN_K, MAX_K].

    Args:
        value: Raw value from request JSON.

    Returns:
        ValidationResult
    """
    if value is None:
        return ValidationResult(False, "Missing required field: 'k'.")
    try:
        k = int(value)
    except (TypeError, ValueError):
        return ValidationResult(False, f"'k' must be an integer, got: {value!r}.")
    if k < MIN_K:
        return ValidationResult(False, f"'k' must be >= {MIN_K}, got: {k}.")
    if k > MAX_K:
        return ValidationResult(False, f"'k' must be <= {MAX_K}, got: {k}.")
    return ValidationResult(True)


def validate_recommendations_count(value: Any) -> ValidationResult:
    """
    Validate the recommendations (top-N count) field.

    Rules:
      - Must be present.
      - Must be an integer in [MIN_RECOMMENDATIONS, MAX_RECOMMENDATIONS].

    Args:
        value: Raw value from request JSON.

    Returns:
        ValidationResult
    """
    if value is None:
        return ValidationResult(False, "Missing required field: 'recommendations'.")
    try:
        n = int(value)
    except (TypeError, ValueError):
        return ValidationResult(
            False, f"'recommendations' must be an integer, got: {value!r}."
        )
    if n < MIN_RECOMMENDATIONS:
        return ValidationResult(
            False, f"'recommendations' must be >= {MIN_RECOMMENDATIONS}, got: {n}."
        )
    if n > MAX_RECOMMENDATIONS:
        return ValidationResult(
            False, f"'recommendations' must be <= {MAX_RECOMMENDATIONS}, got: {n}."
        )
    return ValidationResult(True)


# ─── Composite validator ──────────────────────────────────────────────────────

def validate_recommend_request(body: dict | None) -> ValidationResult:
    """
    Validate the entire POST /recommend request body.

    Checks each required field in order and returns the first failure.

    Args:
        body: Parsed JSON dict from flask.request.get_json().
              May be None if the request had no JSON body.

    Returns:
        ValidationResult — valid only when all three fields pass.
    """
    if not body:
        return ValidationResult(False, "Request body is missing or not valid JSON.")

    for validator, key in [
        (validate_user_id,             "user_id"),
        (validate_k,                   "k"),
        (validate_recommendations_count, "recommendations"),
    ]:
        result = validator(body.get(key))
        if not result:
            return result

    return ValidationResult(True)

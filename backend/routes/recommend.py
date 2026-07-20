"""
routes/recommend.py
--------------------
Blueprint for the movie recommendation endpoint.

POST /recommend
---------------
Request body (JSON)
    {
        "user_id":        4,
        "k":              6,
        "recommendations": 10
    }

Success response (HTTP 200)
    {
        "success": true,
        "recommendations": [
            {
                "title":               "Toy Story (1995)",
                "year":                1995,
                "genres":              ["Animation", "Comedy", "Fantasy"],
                "predicted_rating":    4.82,
                "similar_users_count": 5
            },
            ...
        ],
        "user_id":   4,
        "k":         6,
        "count":     10
    }

Error responses
    HTTP 400 — validation failure or user not in matrix
    HTTP 500 — internal error
"""

import time
from flask import Blueprint, request

from services.recommender import get_recommendations_for_user
from utils.validators import validate_recommend_request
from utils.helpers import success_response, error_response
from utils.logger import get_logger

logger = get_logger(__name__)

recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    """
    POST /recommend

    Validates request parameters, generates recommendations using the
    KNN collaborative filtering pipeline, and returns ranked results.
    """
    start_time = time.perf_counter()

    # ── 1. Parse request body ─────────────────────────────────────────────────
    body = request.get_json(silent=True)

    # ── 2. Validate all fields ────────────────────────────────────────────────
    validation = validate_recommend_request(body)
    if not validation:
        logger.warning("POST /recommend — validation failed: %s", validation.message)
        return error_response(validation.message, 400)

    user_id          = int(body["user_id"])
    k                = int(body["k"])
    n_recommendations = int(body["recommendations"])

    logger.info(
        "POST /recommend — user_id=%d, k=%d, n=%d",
        user_id, k, n_recommendations,
    )

    # ── 3. Generate recommendations ───────────────────────────────────────────
    try:
        recommendations, error_msg = get_recommendations_for_user(
            user_id=user_id,
            k=k,
            n_recommendations=n_recommendations,
        )
    except Exception as exc:
        logger.exception("Unhandled exception in POST /recommend")
        return error_response("Recommendation generation failed.", 500)

    # ── 4. Handle service-level errors ────────────────────────────────────────
    if error_msg:
        return error_response(error_msg, 400)

    if not recommendations:
        return error_response("No recommendations could be generated for this user.", 400)

    # ── 5. Build and return response ──────────────────────────────────────────
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "POST /recommend — returned %d results for user_id=%d in %.1f ms",
        len(recommendations), user_id, elapsed_ms,
    )

    return success_response({
        "recommendations": recommendations,
        "user_id":         user_id,
        "k":               k,
        "count":           len(recommendations),
        "elapsed_ms":      round(elapsed_ms, 1),
    })

"""
services/recommender.py
-----------------------
Orchestration layer between the route handler and the recommendation engine.

Responsibilities:
  - Accept raw validated parameters from the route
  - Check user existence in the matrix
  - Delegate to recommendation_engine.generate_recommendations()
  - Wrap results into the response schema expected by the frontend
  - Log execution metadata

This layer keeps routes/recommend.py thin (HTTP concerns only) and
keeps recommendation_engine.py pure (ML concerns only).
"""

from utils.logger import get_logger
from utils.helpers import timer
from services.recommendation_engine import generate_recommendations, user_exists

logger = get_logger(__name__)


def get_recommendations_for_user(
    user_id: int,
    k: int,
    n_recommendations: int,
) -> tuple[list[dict], str | None]:
    """
    Produce recommendations for a user or return an error message.

    Args:
        user_id:          Target user ID.
        k:                Number of KNN nearest neighbours.
        n_recommendations: How many movies to return.

    Returns:
        Tuple of (recommendations, error_message).
          - If successful: (list_of_dicts, None)
          - If failed:     ([], error_message_str)

    Each recommendation dict has the structure:
        {
            "title":               str,
            "year":                int | None,
            "genres":              list[str],
            "predicted_rating":    float,
            "similar_users_count": int,
        }
    """
    logger.info(
        "Recommendation request — user_id=%d, k=%d, n=%d",
        user_id, k, n_recommendations,
    )

    # ── Check user exists in matrix ───────────────────────────────────────────
    if not user_exists(user_id):
        msg = (
            f"User ID {user_id} does not exist in the recommendation matrix. "
            "Only users with sufficient rating history are supported. "
            "Try one of the valid user IDs from the dataset."
        )
        logger.warning(msg)
        return [], msg

    # ── Generate recommendations ──────────────────────────────────────────────
    try:
        with timer(f"Full recommendation pipeline (user={user_id})"):
            recommendations = generate_recommendations(
                user_id=user_id,
                k=k,
                n_recommendations=n_recommendations,
            )
    except ValueError as exc:
        # Raised by engine when user not in matrix (secondary guard)
        logger.warning("ValueError during recommendation: %s", exc)
        return [], str(exc)
    except Exception as exc:
        logger.exception("Unexpected error during recommendation for user_id=%d", user_id)
        return [], "Recommendation generation failed due to an internal error."

    if not recommendations:
        return [], "No recommendations could be generated for this user."

    return recommendations, None

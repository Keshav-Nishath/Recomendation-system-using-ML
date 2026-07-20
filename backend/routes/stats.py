"""
routes/stats.py
---------------
Blueprint for the dataset statistics endpoint.

GET /stats
----------
Returns dataset summary statistics displayed in the Streamlit
frontend sidebar.

Response schema
---------------
{
    "success":       true,
    "users":         7977,
    "movies":        9087,
    "total_ratings": 22884377,
    "avg_rating":    3.53
}
"""

import config
from flask import Blueprint

from utils.helpers import success_response, error_response
from utils.logger import get_logger

logger = get_logger(__name__)

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/stats", methods=["GET"])
def get_stats():
    """
    GET /stats

    Returns pre-computed dataset statistics cached in config.STATS.
    Statistics are calculated once at startup by data_loader.load_datasets().
    """
    logger.info("GET /stats")

    if not config.STATS:
        return error_response("Statistics not yet available — server is starting up.", 503)

    return success_response({
        "users":          config.STATS.get("users", 0),
        "movies":         config.STATS.get("movies", 0),
        "total_ratings":  config.STATS.get("total_ratings", 0),
        "avg_rating":     config.STATS.get("avg_rating", 0.0),
        # Map keys that the frontend api/client.py expects
        "active_users":   config.STATS.get("users", 0),
        "ratings":        config.STATS.get("total_ratings", 0),
    })

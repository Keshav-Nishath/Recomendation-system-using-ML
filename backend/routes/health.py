"""
routes/health.py
----------------
Blueprint for the health-check endpoint.

GET /health
-----------
Returns the operational status of all backend subsystems.
Used by the Streamlit frontend sidebar to display system-status cards.

Response schema
---------------
{
    "status":                  "healthy" | "degraded",
    "recommendation_engine":   true | false,
    "similarity_matrix":       true | false,
    "dataset":                 true | false,
    "system":                  true | false
}
"""

from flask import Blueprint

from models.knn_loader import is_loaded as knn_is_loaded
from services.data_loader import is_data_loaded
from utils.helpers import success_response
from utils.logger import get_logger

logger = get_logger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /health

    Returns a JSON summary of subsystem readiness.
    HTTP 200 when healthy; HTTP 503 when any subsystem is not ready.
    """
    logger.info("GET /health")

    model_ok   = knn_is_loaded()
    dataset_ok = is_data_loaded()
    all_ok     = model_ok and dataset_ok

    payload = {
        "status":                 "healthy" if all_ok else "degraded",
        "recommendation_engine":  model_ok,
        "similarity_matrix":      model_ok,
        "dataset":                dataset_ok,
        "system":                 all_ok,
    }

    http_status = 200 if all_ok else 503
    return success_response(payload, status_code=http_status)

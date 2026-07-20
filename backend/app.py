"""
app.py
------
CineMatch Flask Backend — Entry Point

Startup sequence:
  1. Configure sys.path so all backend modules import cleanly
  2. Create the Flask app
  3. Configure CORS
  4. Load KNN model + user-item matrix (knn.pkl, matrix.pkl)
  5. Load all CSV datasets (movies, ratings, links, tags)
  6. Register route blueprints
  7. Start the server

Run with:
    python app.py
"""

import sys
import os
import time

# ─── Ensure backend/ is on sys.path ─────────────────────────────────────────
# This allows every sub-module to use absolute imports (from config import ...)
# regardless of where `python app.py` is invoked from.
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

# ─── Flask imports ────────────────────────────────────────────────────────────
from flask import Flask, jsonify
from flask_cors import CORS

# ─── Internal imports ─────────────────────────────────────────────────────────
import config
from utils.logger import get_logger
from utils.helpers import error_response

logger = get_logger(__name__)


# ─── Application factory ──────────────────────────────────────────────────────

def create_app() -> Flask:
    """
    Create, configure, and return the Flask application.

    All startup I/O (pickle loading, CSV loading) happens here so that
    the server is ready to serve requests from the first HTTP call.
    """
    app = Flask(__name__)

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Allow the Streamlit frontend to call the API from any origin.
    # CORS(app) with no arguments enables all origins — suitable for development.
    # For production, pass origins=config.CORS_ORIGINS to restrict access.
    CORS(app)
    logger.info("CORS enabled — allowed origins: %s", config.CORS_ORIGINS)

    # ── Global error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"success": False, "message": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify({"success": False, "message": "HTTP method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(_e):
        logger.exception("Unhandled 500 error")
        return jsonify({"success": False, "message": "Internal server error."}), 500

    # ── Load ML artifacts ─────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("CineMatch Backend  v1.0")
    logger.info("Starting up…")
    logger.info("=" * 60)

    startup_start = time.perf_counter()

    from models.knn_loader import load_artifacts
    try:
        load_artifacts()
    except RuntimeError as exc:
        logger.critical("FATAL: Could not load ML artifacts — %s", exc)
        raise SystemExit(1) from exc

    # ── Load datasets ─────────────────────────────────────────────────────────
    from services.data_loader import load_datasets
    try:
        load_datasets()
    except RuntimeError as exc:
        logger.critical("FATAL: Could not load datasets — %s", exc)
        raise SystemExit(1) from exc

    startup_elapsed = (time.perf_counter() - startup_start) * 1000
    logger.info("=" * 60)
    logger.info("All artifacts and datasets loaded in %.1f ms.", startup_elapsed)
    logger.info("CineMatch Backend is READY.")
    logger.info("=" * 60)

    # ── Register blueprints ───────────────────────────────────────────────────
    from routes.health    import health_bp
    from routes.stats     import stats_bp
    from routes.recommend import recommend_bp
    from routes.user      import user_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(user_bp)

    logger.info(
        "Blueprints registered: %s",
        [r.rule for r in app.url_map.iter_rules()],
    )

    return app


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    flask_app = create_app()

    logger.info(
        "Starting Flask server on %s:%d  (debug=%s)",
        config.HOST, config.PORT, config.DEBUG,
    )
    flask_app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )

"""
config.py
---------
All configurable values for the CineMatch Flask backend.
No file paths or tuning parameters are hardcoded anywhere else.
"""

import os

# ─── Project Root ─────────────────────────────────────────────────────────────
# backend/ lives one level below the project root where the data files are.
_BACKEND_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT  = os.path.dirname(_BACKEND_DIR)

# ─── Server ───────────────────────────────────────────────────────────────────
HOST  = "0.0.0.0"
PORT  = 5000
DEBUG = False           # set to True for development hot-reload

# ─── Data File Paths ──────────────────────────────────────────────────────────
# All data files live in the project root (symlinking failed on this machine).
DATA_DIR         = PROJECT_ROOT

KNN_MODEL_PATH   = os.path.join(DATA_DIR, "knn.pkl")
MATRIX_PATH      = os.path.join(DATA_DIR, "matrix.pkl")
MOVIES_CSV_PATH  = os.path.join(DATA_DIR, "movies.csv")
RATINGS_CSV_PATH = os.path.join(DATA_DIR, "ratings.csv")
LINKS_CSV_PATH   = os.path.join(DATA_DIR, "links.csv")
TAGS_CSV_PATH    = os.path.join(DATA_DIR, "tags.csv")

# ─── Recommendation Defaults ──────────────────────────────────────────────────
DEFAULT_K                   = 6
DEFAULT_RECOMMENDATIONS     = 10

# ─── Validation Bounds ───────────────────────────────────────────────────────
MIN_K                   = 1
MAX_K                   = 50          # guard against very slow KNN queries
MIN_RECOMMENDATIONS     = 1
MAX_RECOMMENDATIONS     = 100

# ─── KNN Behaviour ───────────────────────────────────────────────────────────
# When running kneighbors we query k+1 neighbours to include the target user
# (who is always the closest to themselves) and then discard the first result.
KNN_EXTRA_NEIGHBOURS = 1

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL  = "INFO"
LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allow the Streamlit frontend (any origin during development).
# Restrict to specific origin(s) in production.
CORS_ORIGINS = "*"

# ─── Dataset Statistics (computed once at startup, cached here) ───────────────
# These are filled in by data_loader.py after loading; treated as mutable globals.
STATS: dict = {}

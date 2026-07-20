"""
models/knn_loader.py
--------------------
Loads and exposes the trained KNN model and user-item matrix.

Both artifacts are loaded exactly once at application startup and kept
in module-level variables.  No other module should ever call pickle.load
on these files directly.

Artifact details (confirmed from inspection):
  knn.pkl
    Type:      sklearn.neighbors.NearestNeighbors
    Metric:    cosine
    Algorithm: brute
    n_samples: 7977
    n_features: 9087  (= number of movies in the matrix)

  matrix.pkl
    Type:      pandas.DataFrame
    Shape:     (7977, 9087)
    Index:     userId  (int64)  — only 7977 unique users have enough ratings
    Columns:   movie title  (str)
    Values:    user ratings 0.5–5.0  (0.0 = not rated)
"""

import pickle
from typing import Optional

import pandas as pd
from sklearn.neighbors import NearestNeighbors

from config import KNN_MODEL_PATH, MATRIX_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


# ─── Module-level singletons ──────────────────────────────────────────────────
# These are None until load_artifacts() is called during Flask startup.

_knn_model: Optional[NearestNeighbors] = None
_matrix:    Optional[pd.DataFrame]     = None
_loaded:    bool                       = False


# ─── Loader ───────────────────────────────────────────────────────────────────

def load_artifacts() -> None:
    """
    Load knn.pkl and matrix.pkl from disk into memory.

    Must be called once before any recommendation request is served.
    Raises RuntimeError if either file cannot be loaded.
    """
    global _knn_model, _matrix, _loaded

    logger.info("Loading KNN model from: %s", KNN_MODEL_PATH)
    try:
        with open(KNN_MODEL_PATH, "rb") as f:
            _knn_model = pickle.load(f)
        logger.info(
            "KNN model loaded — metric=%s, algorithm=%s, n_samples=%d, n_features=%d",
            _knn_model.metric,
            _knn_model.algorithm,
            _knn_model.n_samples_fit_,
            _knn_model.n_features_in_,
        )
    except FileNotFoundError:
        raise RuntimeError(f"KNN model file not found: {KNN_MODEL_PATH}")
    except Exception as exc:
        raise RuntimeError(f"Failed to load KNN model: {exc}") from exc

    logger.info("Loading user-item matrix from: %s", MATRIX_PATH)
    try:
        with open(MATRIX_PATH, "rb") as f:
            _matrix = pickle.load(f)
        logger.info(
            "Matrix loaded — shape=%s, index='%s', dtype=%s",
            _matrix.shape,
            _matrix.index.name,
            _matrix.index.dtype,
        )
    except FileNotFoundError:
        raise RuntimeError(f"Matrix file not found: {MATRIX_PATH}")
    except Exception as exc:
        raise RuntimeError(f"Failed to load matrix: {exc}") from exc

    _loaded = True
    logger.info("All ML artifacts loaded successfully.")


# ─── Accessors ────────────────────────────────────────────────────────────────

def get_knn_model() -> NearestNeighbors:
    """
    Return the loaded KNN model.

    Raises:
        RuntimeError: if load_artifacts() has not been called yet.
    """
    if _knn_model is None:
        raise RuntimeError("KNN model is not loaded. Call load_artifacts() first.")
    return _knn_model


def get_matrix() -> pd.DataFrame:
    """
    Return the user-item rating matrix DataFrame.

    Raises:
        RuntimeError: if load_artifacts() has not been called yet.
    """
    if _matrix is None:
        raise RuntimeError("Matrix is not loaded. Call load_artifacts() first.")
    return _matrix


def is_loaded() -> bool:
    """Return True if both artifacts have been loaded successfully."""
    return _loaded

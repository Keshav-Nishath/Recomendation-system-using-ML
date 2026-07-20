"""
services/data_loader.py
-----------------------
Loads all CSV datasets into memory once at Flask startup.

Datasets loaded:
  movies.csv    — movieId, title, genres
  ratings.csv   — userId, movieId, rating, timestamp
  links.csv     — movieId, imdbId, tmdbId
  tags.csv      — userId, movieId, tag, timestamp

Also builds derived lookup structures used by the recommendation engine:
  title_to_genres   dict[str, str]   — movie title → raw genres string
  title_to_genres_list dict[str, list[str]] — title → split genre list
  title_to_year     dict[str, int|None]

Computes and caches dataset statistics exposed by GET /stats.
"""

from typing import Optional

import pandas as pd

import config
from utils.logger import get_logger
from utils.helpers import split_genres, extract_year

logger = get_logger(__name__)


# ─── Module-level singletons ──────────────────────────────────────────────────

_movies_df:  Optional[pd.DataFrame] = None
_ratings_df: Optional[pd.DataFrame] = None
_links_df:   Optional[pd.DataFrame] = None
_tags_df:    Optional[pd.DataFrame] = None

# Derived lookups (built once, used by recommendation engine)
_title_to_genres:      dict[str, str]          = {}
_title_to_genres_list: dict[str, list[str]]    = {}
_title_to_year:        dict[str, Optional[int]] = {}

_data_loaded: bool = False


# ─── Loader ───────────────────────────────────────────────────────────────────

def load_datasets() -> None:
    """
    Load all CSV files and build derived lookup structures.
    Populates config.STATS with summary statistics.

    Must be called once at startup after load_artifacts() completes.
    Raises RuntimeError if any required file is missing.
    """
    global _movies_df, _ratings_df, _links_df, _tags_df
    global _title_to_genres, _title_to_genres_list, _title_to_year
    global _data_loaded

    # ── movies.csv ────────────────────────────────────────────────────────────
    logger.info("Loading movies.csv from: %s", config.MOVIES_CSV_PATH)
    try:
        _movies_df = pd.read_csv(config.MOVIES_CSV_PATH)
        logger.info("movies.csv loaded — %d rows", len(_movies_df))
    except FileNotFoundError:
        raise RuntimeError(f"movies.csv not found: {config.MOVIES_CSV_PATH}")

    # ── ratings.csv ───────────────────────────────────────────────────────────
    logger.info("Loading ratings.csv from: %s", config.RATINGS_CSV_PATH)
    try:
        _ratings_df = pd.read_csv(config.RATINGS_CSV_PATH)
        logger.info("ratings.csv loaded — %d rows", len(_ratings_df))
    except FileNotFoundError:
        raise RuntimeError(f"ratings.csv not found: {config.RATINGS_CSV_PATH}")

    # ── links.csv ─────────────────────────────────────────────────────────────
    logger.info("Loading links.csv from: %s", config.LINKS_CSV_PATH)
    try:
        _links_df = pd.read_csv(config.LINKS_CSV_PATH)
        logger.info("links.csv loaded — %d rows", len(_links_df))
    except FileNotFoundError:
        raise RuntimeError(f"links.csv not found: {config.LINKS_CSV_PATH}")

    # ── tags.csv ──────────────────────────────────────────────────────────────
    logger.info("Loading tags.csv from: %s", config.TAGS_CSV_PATH)
    try:
        _tags_df = pd.read_csv(config.TAGS_CSV_PATH)
        logger.info("tags.csv loaded — %d rows", len(_tags_df))
    except FileNotFoundError:
        logger.warning("tags.csv not found — continuing without tags.")
        _tags_df = pd.DataFrame(columns=["userId", "movieId", "tag", "timestamp"])

    # ── Build derived lookups ─────────────────────────────────────────────────
    logger.info("Building title lookup tables...")
    for _, row in _movies_df.iterrows():
        title  = str(row["title"])
        genres = str(row["genres"])
        _title_to_genres[title]           = genres
        _title_to_genres_list[title]      = split_genres(genres)
        _title_to_year[title]             = extract_year(title)
    logger.info("Title lookups built for %d movies.", len(_title_to_genres))

    # ── Dataset statistics ────────────────────────────────────────────────────
    # These are reported by GET /stats.  We use matrix dimensions for
    # users/movies (what the model actually knows) and ratings.csv for totals.
    from models.knn_loader import get_matrix
    matrix = get_matrix()

    config.STATS = {
        "users":         int(matrix.shape[0]),       # users in model: 7977
        "movies":        int(matrix.shape[1]),       # movies in model: 9087
        "total_ratings": int(len(_ratings_df)),      # all ratings: 22.8M
        "avg_rating":    round(float(_ratings_df["rating"].mean()), 2),
        # also expose raw CSV counts for reference
        "movies_csv_count": int(len(_movies_df)),
    }
    logger.info(
        "Stats computed — users=%d, movies=%d, ratings=%d, avg_rating=%.2f",
        config.STATS["users"],
        config.STATS["movies"],
        config.STATS["total_ratings"],
        config.STATS["avg_rating"],
    )

    _data_loaded = True
    logger.info("All datasets loaded successfully.")


# ─── Accessors ────────────────────────────────────────────────────────────────

def get_movies_df() -> pd.DataFrame:
    _require_loaded()
    return _movies_df


def get_ratings_df() -> pd.DataFrame:
    _require_loaded()
    return _ratings_df


def get_links_df() -> pd.DataFrame:
    _require_loaded()
    return _links_df


def get_tags_df() -> pd.DataFrame:
    _require_loaded()
    return _tags_df


def get_title_to_genres() -> dict[str, str]:
    """Return raw genres string keyed by movie title."""
    _require_loaded()
    return _title_to_genres


def get_title_to_genres_list() -> dict[str, list[str]]:
    """Return split genre list keyed by movie title."""
    _require_loaded()
    return _title_to_genres_list


def get_title_to_year() -> dict[str, Optional[int]]:
    """Return integer year keyed by movie title (None if not extractable)."""
    _require_loaded()
    return _title_to_year


def is_data_loaded() -> bool:
    return _data_loaded


# ─── Internal ─────────────────────────────────────────────────────────────────

def _require_loaded() -> None:
    if not _data_loaded:
        raise RuntimeError("Datasets are not loaded. Call load_datasets() first.")

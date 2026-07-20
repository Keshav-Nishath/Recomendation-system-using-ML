"""
services/recommendation_engine.py
-----------------------------------
Core recommendation pipeline.

Implements the full KNN-based User Collaborative Filtering workflow
described in backend.md §10-11:

  1.  Receive user_id, k, n_recommendations
  2.  Retrieve user vector from matrix
  3.  Query KNN model → find k similar users
  4.  Collect all movies rated by those neighbours
  5.  Remove movies already rated by the target user
  6.  Score remaining movies using similarity-weighted mean rating
  7.  Return the top-N ranked movies with metadata

Scoring strategy
----------------
For each candidate movie we compute a **similarity-weighted mean rating**:

    score(movie) = Σ(similarity_i * rating_i) / Σ(similarity_i)

where the sum runs over neighbours that have rated the movie.

Similarity is derived from the cosine distance returned by kneighbors:
    similarity = 1 - distance  (∈ [0, 1])

This rewards movies that are highly rated by neighbours who are most
similar to the target user, and naturally down-weights movies rated only
by distant neighbours.
"""

import numpy as np
import pandas as pd
import scipy.sparse as sp
from typing import Optional

from models.knn_loader import get_knn_model, get_matrix
from services.data_loader import get_title_to_genres_list, get_title_to_year
from utils.logger import get_logger
from utils.helpers import timer

logger = get_logger(__name__)


# ─── Public entry point ────────────────────────────────────────────────────────

def generate_recommendations(
    user_id: int,
    k: int,
    n_recommendations: int,
) -> list[dict]:
    """
    Generate movie recommendations for an existing user.

    Args:
        user_id:          Target user (must exist in matrix.index).
        k:                Number of nearest neighbours to query.
        n_recommendations: Maximum number of movies to return.

    Returns:
        List of recommendation dicts, sorted by predicted rating descending.
        Each dict contains:
            title                str
            year                 int | None
            genres               list[str]
            predicted_rating     float
            similar_users_count  int

    Raises:
        ValueError: if user_id is not present in the matrix.
    """
    matrix = get_matrix()
    knn    = get_knn_model()

    # ── Step 1: locate user in matrix ─────────────────────────────────────────
    if user_id not in matrix.index:
        raise ValueError(
            f"User ID {user_id} is not in the recommendation matrix. "
            "Only users with sufficient rating history are supported."
        )

    user_idx = matrix.index.get_loc(user_id)
    logger.info(
        "Generating recommendations — user_id=%d (matrix_row=%d), k=%d, top_n=%d",
        user_id, user_idx, k, n_recommendations,
    )

    # ── Step 2: retrieve user vector ──────────────────────────────────────────
    # Convert to sparse CSR — the KNN model was trained on a sparse matrix
    # (scipy.sparse.csr_matrix), so the query must also be sparse or sklearn
    # will raise a ValueError about input format mismatch.
    user_vector = sp.csr_matrix(matrix.iloc[user_idx].values.reshape(1, -1))

    # ── Step 3: query KNN ─────────────────────────────────────────────────────
    # Request k+1 neighbours because the first result is always the user
    # themselves (distance ≈ 0).
    n_query = min(k + 1, matrix.shape[0])  # can't request more rows than exist

    with timer("KNN kneighbors query"):
        distances, indices = knn.kneighbors(user_vector, n_neighbors=n_query)

    distances = distances[0]   # shape (n_query,)
    indices   = indices[0]     # shape (n_query,)

    # ── Step 4: identify neighbours (skip self) ────────────────────────────────
    # The nearest neighbour at index 0 is typically the user themselves
    # (distance ≈ 0).  We drop any index whose matrix userId equals user_id.
    neighbour_data: list[tuple[int, float]] = []   # (matrix_row_idx, similarity)
    for dist, idx in zip(distances, indices):
        neighbour_uid = matrix.index[idx]
        if int(neighbour_uid) == user_id:
            continue
        similarity = max(0.0, 1.0 - float(dist))  # cosine similarity
        neighbour_data.append((idx, similarity))
        if len(neighbour_data) >= k:
            break

    if not neighbour_data:
        logger.warning("No neighbours found for user_id=%d", user_id)
        return []

    logger.info(
        "Found %d neighbours for user_id=%d  (sims: %s)",
        len(neighbour_data),
        user_id,
        [f"{s:.3f}" for _, s in neighbour_data],
    )

    # ── Step 5: movies already rated by the target user ───────────────────────
    user_row         = matrix.iloc[user_idx]
    already_rated    = set(matrix.columns[user_row.values > 0].tolist())
    logger.info("User %d already rated %d movies.", user_id, len(already_rated))

    # ── Step 6: collect neighbour ratings for unseen movies ───────────────────
    # For each candidate title, accumulate weighted rating and weight sum.
    weighted_sum:   dict[str, float] = {}   # title → Σ(sim * rating)
    weight_total:   dict[str, float] = {}   # title → Σ(sim)
    supporter_count: dict[str, int]  = {}   # title → # neighbours who rated it

    for row_idx, similarity in neighbour_data:
        neighbour_row  = matrix.iloc[row_idx]
        rated_mask     = neighbour_row.values > 0
        rated_titles   = matrix.columns[rated_mask].tolist()
        rated_ratings  = neighbour_row.values[rated_mask].tolist()

        for title, rating in zip(rated_titles, rated_ratings):
            if title in already_rated:
                continue                  # skip movies the user has already seen
            if title not in weighted_sum:
                weighted_sum[title]    = 0.0
                weight_total[title]    = 0.0
                supporter_count[title] = 0
            weighted_sum[title]    += similarity * float(rating)
            weight_total[title]    += similarity
            supporter_count[title] += 1

    logger.info(
        "Candidate pool after filtering already-rated: %d movies.", len(weighted_sum)
    )

    if not weighted_sum:
        logger.warning("No candidate movies left after filtering for user_id=%d", user_id)
        return []

    # ── Step 7: score and rank ─────────────────────────────────────────────────
    title_to_genres_list = get_title_to_genres_list()
    title_to_year        = get_title_to_year()

    scored: list[dict] = []
    for title, w_sum in weighted_sum.items():
        w_total = weight_total[title]
        if w_total <= 0:
            continue
        predicted_rating = w_sum / w_total          # similarity-weighted mean
        genres_list      = title_to_genres_list.get(title, [])
        year             = title_to_year.get(title)

        scored.append({
            "title":               title,
            "year":                year,
            "genres":              genres_list,          # list[str] — frontend expects a list
            "predicted_rating":    round(predicted_rating, 2),  # was "rating"
            "similar_users_count": supporter_count[title],      # was "similar_users"
        })

    # Sort by predicted rating descending, then by supporter count descending
    # as a secondary tie-breaker.
    scored.sort(key=lambda x: (x["predicted_rating"], x["similar_users_count"]), reverse=True)

    top_n = scored[:n_recommendations]
    logger.info(
        "Returning %d recommendations for user_id=%d  (top rating: %.2f)",
        len(top_n),
        user_id,
        top_n[0]["predicted_rating"] if top_n else 0,
    )
    return top_n


# ─── User existence check ─────────────────────────────────────────────────────

def user_exists(user_id: int) -> bool:
    """
    Return True if the user_id is present in the recommendation matrix.

    Only ~7977 users have enough rating history to be in the matrix.
    This is separate from whether the user appears in ratings.csv.
    """
    return int(user_id) in get_matrix().index

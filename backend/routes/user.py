"""
routes/user.py
--------------
Blueprint for user-related endpoints.

GET /user/<user_id>/profile
---------------------------
Returns a profile summary for the given user, built from ratings.csv
and the recommendation matrix (matrix.pkl).

Success response (HTTP 200)
    {
        "success":      true,
        "user_id":      17,
        "num_ratings":  305,
        "avg_rating":   3.94,
        "highly_rated": [
            {
                "title":  "Schindler's List (1993)",
                "year":   1993,
                "rating": 5.0,
                "genres": ["Drama", "War"]
            },
            ...
        ]
    }

Error responses
    HTTP 400 — invalid or missing user_id
    HTTP 404 — user not found in ratings.csv
    HTTP 500 — internal error


GET /user/<user_id>/validate
----------------------------
Returns whether a user_id exists in the recommendation matrix.

Success response (HTTP 200)
    { "valid": true,  "message": "User found in dataset." }
    { "valid": false, "message": "User ID ... not found." }
"""

from flask import Blueprint

from services.data_loader import get_ratings_df, get_title_to_genres_list, get_title_to_year
from models.knn_loader import get_matrix
from utils.helpers import success_response, error_response
from utils.logger import get_logger

logger = get_logger(__name__)

user_bp = Blueprint("user", __name__)

# How many top-rated movies to include in the profile response
_HIGHLY_RATED_LIMIT = 5
_HIGHLY_RATED_MIN_RATING = 4.0   # only include ratings ≥ this threshold


# ─── /user/<user_id>/profile ──────────────────────────────────────────────────

@user_bp.route("/user/<int:user_id>/profile", methods=["GET"])
def user_profile(user_id: int):
    """
    GET /user/<user_id>/profile

    Computes:
      - num_ratings  — total ratings the user has given in ratings.csv
      - avg_rating   — their mean rating (rounded to 2 dp)
      - highly_rated — up to 5 movies they rated ≥ 4.0, sorted by rating desc
    """
    if user_id <= 0:
        return error_response("'user_id' must be a positive integer.", 400)

    logger.info("GET /user/%d/profile", user_id)

    try:
        ratings_df           = get_ratings_df()
        title_to_genres_list = get_title_to_genres_list()
        title_to_year        = get_title_to_year()
        matrix               = get_matrix()
    except RuntimeError as exc:
        logger.error("Data not loaded: %s", exc)
        return error_response("Backend data not yet loaded.", 503)

    # ── Filter to this user ───────────────────────────────────────────────────
    user_ratings = ratings_df[ratings_df["userId"] == user_id]

    if user_ratings.empty:
        return error_response(
            f"User ID {user_id} was not found in the ratings dataset.", 404
        )

    num_ratings = int(len(user_ratings))
    avg_rating  = round(float(user_ratings["rating"].mean()), 2)

    # ── Build highly-rated list from the matrix (title-indexed) ──────────────
    # The matrix columns are movie titles; we use it to resolve titles for
    # movie IDs the user rated highly.  We join on movieId via links if needed,
    # but the simplest path is: matrix columns = titles, ratings.csv has movieId.
    # We resolve movieId → title via movies.csv (already loaded in title lookups).

    # Build a reverse lookup: movieId → title from the data_loader movies_df
    from services.data_loader import get_movies_df
    movies_df = get_movies_df()
    movie_id_to_title = dict(zip(movies_df["movieId"], movies_df["title"]))

    # Find highly-rated movies for this user (rating ≥ threshold)
    high = user_ratings[user_ratings["rating"] >= _HIGHLY_RATED_MIN_RATING].copy()
    high = high.sort_values("rating", ascending=False).head(_HIGHLY_RATED_LIMIT)

    highly_rated = []
    for _, row in high.iterrows():
        title  = movie_id_to_title.get(int(row["movieId"]), None)
        if title is None:
            continue
        genres = title_to_genres_list.get(title, [])
        year   = title_to_year.get(title)
        highly_rated.append({
            "title":  title,
            "year":   year,
            "rating": float(row["rating"]),
            "genres": genres,
        })

    logger.info(
        "Profile for user_id=%d — num_ratings=%d, avg=%.2f, highly_rated=%d",
        user_id, num_ratings, avg_rating, len(highly_rated),
    )

    return success_response({
        "user_id":      user_id,
        "num_ratings":  num_ratings,
        "avg_rating":   avg_rating,
        "highly_rated": highly_rated,
    })


# ─── /user/<user_id>/validate ─────────────────────────────────────────────────

@user_bp.route("/user/<int:user_id>/validate", methods=["GET"])
def validate_user(user_id: int):
    """
    GET /user/<user_id>/validate

    Returns whether the user exists in the recommendation matrix
    (i.e. has enough rating history to receive recommendations).
    """
    if user_id <= 0:
        return {"valid": False, "message": "User ID must be a positive integer."}, 400

    logger.info("GET /user/%d/validate", user_id)

    try:
        matrix = get_matrix()
    except RuntimeError:
        return {"valid": False, "message": "Backend data not yet loaded."}, 503

    if int(user_id) in matrix.index:
        return {"valid": True, "message": "User found in dataset."}
    return {"valid": False, "message": f"User ID {user_id} not found in the recommendation matrix."}

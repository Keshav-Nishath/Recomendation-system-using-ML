"""
api/client.py
-------------
API client for CineMatch.

Currently uses MOCK responses to simulate the Flask backend.
Every function is documented with a TODO comment indicating the
real endpoint that will replace the mock when the backend is live.

Pattern:
  - Each function first tries the real HTTP endpoint.
  - If the backend is unavailable (ConnectionError / timeout), it falls
    back to the mock data so the UI keeps working during development.
"""

import random
import time
import requests
from config import BACKEND_BASE_URL, API_ENDPOINTS


# ─── Timeout for all real HTTP requests ──────────────────────────────────────
REQUEST_TIMEOUT = 5   # seconds


# ─── Mock Data ────────────────────────────────────────────────────────────────

_MOCK_STATS = {
    "active_users": 92_391,
    "movies":       3_706,
    "ratings":      1_000_209,
    "avg_rating":   3.58,
}

_MOCK_STATUS = {
    "recommendation_engine": True,
    "similarity_matrix":     True,
    "dataset":               True,
    "system":                True,
}

# A small pool of fake movie data for mock recommendations
_MOCK_MOVIES = [
    {
        "movie_id": 1,
        "title": "Toy Story",
        "year": 1995,
        "genres": ["Animation", "Children's", "Comedy"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/862",
    },
    {
        "movie_id": 2,
        "title": "Jumanji",
        "year": 1995,
        "genres": ["Adventure", "Children's", "Fantasy"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/8844",
    },
    {
        "movie_id": 3,
        "title": "The Shawshank Redemption",
        "year": 1994,
        "genres": ["Drama"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/278",
    },
    {
        "movie_id": 4,
        "title": "Pulp Fiction",
        "year": 1994,
        "genres": ["Crime", "Drama", "Thriller"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/680",
    },
    {
        "movie_id": 5,
        "title": "The Silence of the Lambs",
        "year": 1991,
        "genres": ["Drama", "Thriller"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/274",
    },
    {
        "movie_id": 6,
        "title": "Schindler's List",
        "year": 1993,
        "genres": ["Drama", "War"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/424",
    },
    {
        "movie_id": 7,
        "title": "Forrest Gump",
        "year": 1994,
        "genres": ["Comedy", "Drama", "Romance"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/13",
    },
    {
        "movie_id": 8,
        "title": "The Matrix",
        "year": 1999,
        "genres": ["Action", "Sci-Fi", "Thriller"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/603",
    },
    {
        "movie_id": 9,
        "title": "GoodFellas",
        "year": 1990,
        "genres": ["Crime", "Drama"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/769",
    },
    {
        "movie_id": 10,
        "title": "The Usual Suspects",
        "year": 1995,
        "genres": ["Crime", "Thriller"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/629",
    },
    {
        "movie_id": 11,
        "title": "Braveheart",
        "year": 1995,
        "genres": ["Action", "Drama", "War"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/197",
    },
    {
        "movie_id": 12,
        "title": "Se7en",
        "year": 1995,
        "genres": ["Crime", "Drama", "Mystery", "Thriller"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/807",
    },
    {
        "movie_id": 13,
        "title": "American Beauty",
        "year": 1999,
        "genres": ["Drama", "Romance"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/14,",
    },
    {
        "movie_id": 14,
        "title": "Raiders of the Lost Ark",
        "year": 1981,
        "genres": ["Action", "Adventure"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/85",
    },
    {
        "movie_id": 15,
        "title": "Star Wars: Episode IV",
        "year": 1977,
        "genres": ["Action", "Adventure", "Sci-Fi"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/11",
    },
    {
        "movie_id": 16,
        "title": "Titanic",
        "year": 1997,
        "genres": ["Drama", "Romance"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/597",
    },
    {
        "movie_id": 17,
        "title": "Fargo",
        "year": 1996,
        "genres": ["Crime", "Drama", "Thriller"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/275",
    },
    {
        "movie_id": 18,
        "title": "The Truman Show",
        "year": 1998,
        "genres": ["Comedy", "Drama"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/37165",
    },
    {
        "movie_id": 19,
        "title": "Blade Runner",
        "year": 1982,
        "genres": ["Film-Noir", "Sci-Fi", "Thriller"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/78",
    },
    {
        "movie_id": 20,
        "title": "Fight Club",
        "year": 1999,
        "genres": ["Crime", "Drama", "Thriller"],
        "poster_url": None,
        "tmdb_url": "https://www.themoviedb.org/movie/550",
    },
]

_MOCK_REASONS = [
    "Liked by {k} users with similar preferences.",
    "Highly rated by your nearest neighbours.",
    "Frequently watched by users with similar tastes.",
    "Strong collaborative filtering score.",
    "A top pick among users who share your rating history.",
    "Consistently praised by users with matching movie preferences.",
]

_MOCK_HIGHLY_RATED = [
    {"title": "The Godfather",        "year": 1972, "rating": 5.0, "genres": ["Crime", "Drama"]},
    {"title": "The Dark Knight",      "year": 2008, "rating": 4.5, "genres": ["Action", "Crime"]},
    {"title": "Inception",            "year": 2010, "rating": 4.5, "genres": ["Action", "Sci-Fi"]},
    {"title": "Interstellar",         "year": 2014, "rating": 5.0, "genres": ["Adventure", "Drama"]},
    {"title": "The Departed",         "year": 2006, "rating": 4.0, "genres": ["Crime", "Drama"]},
]


# ─── Helper ───────────────────────────────────────────────────────────────────

def _get(url: str, params: dict = None):
    """Perform a GET request with timeout. Returns (data_dict, error_str)."""
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Backend unavailable"
    except requests.exceptions.Timeout:
        return None, "Request timed out"
    except requests.exceptions.HTTPError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


def _post(url: str, payload: dict = None):
    """Perform a POST request with timeout. Returns (data_dict, error_str)."""
    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Backend unavailable"
    except requests.exceptions.Timeout:
        return None, "Request timed out"
    except requests.exceptions.HTTPError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


# ─── Public API Functions ─────────────────────────────────────────────────────

def get_backend_status() -> dict:
    """
    Check whether the Flask backend services are running.

    TODO: Replace mock with real call:
        GET /api/health
        Returns { "recommendation_engine": bool, "similarity_matrix": bool,
                  "dataset": bool, "system": bool }
    """
    data, error = _get(API_ENDPOINTS["health"])
    if data:
        return {"data": data, "error": None, "source": "backend"}

    # Mock fallback
    return {"data": _MOCK_STATUS, "error": None, "source": "mock"}


def get_dataset_stats() -> dict:
    """
    Fetch dataset statistics shown in the sidebar.

    TODO: Replace mock with real call:
        GET /api/stats
        Returns { "active_users": int, "movies": int,
                  "ratings": int, "avg_rating": float }
    """
    data, error = _get(API_ENDPOINTS["stats"])
    if data:
        return {"data": data, "error": None, "source": "backend"}

    # Mock fallback
    return {"data": _MOCK_STATS, "error": None, "source": "mock"}


def get_user_profile(user_id: int) -> dict:
    """
    Fetch the profile context for a given user.

    TODO: Replace mock with real call:
        GET /api/user/<user_id>/profile
        Returns { "user_id": int, "num_ratings": int,
                  "avg_rating": float, "highly_rated": list }
    """
    url = f"{BACKEND_BASE_URL}/user/{user_id}/profile"
    data, error = _get(url)
    if data:
        return {"data": data, "error": None, "source": "backend"}

    # Mock fallback — vary values by user_id so it feels realistic
    random.seed(user_id)
    num_ratings = random.randint(40, 350)
    avg_rating  = round(random.uniform(3.2, 4.8), 2)

    mock_profile = {
        "user_id":     user_id,
        "num_ratings": num_ratings,
        "avg_rating":  avg_rating,
        "highly_rated": random.sample(_MOCK_HIGHLY_RATED, k=min(3, len(_MOCK_HIGHLY_RATED))),
    }
    return {"data": mock_profile, "error": None, "source": "mock"}


def get_recommendations(user_id: int, n_recommendations: int = 10, k_neighbours: int = 6) -> dict:
    """
    Generate movie recommendations for a user.

    TODO: Replace mock with real call:
        POST /api/recommend
        Body: { "user_id": int, "n_recommendations": int, "k_neighbours": int }
        Returns { "recommendations": [ { movie fields + predicted_rating,
                  similar_users_count, reason } ] }
    """
    payload = {
        "user_id":         user_id,
        "recommendations": n_recommendations,   # backend field name
        "k":               k_neighbours,        # backend field name
    }
    data, error = _post(API_ENDPOINTS["recommend"], payload)
    if data:
        return {"data": data, "error": None, "source": "backend"}

    # Mock fallback — deterministic shuffle per user for consistency
    random.seed(user_id * 31)
    pool = _MOCK_MOVIES.copy()
    random.shuffle(pool)
    selected = pool[:min(n_recommendations, len(pool))]

    recommendations = []
    for movie in selected:
        predicted_rating   = round(random.uniform(3.5, 5.0), 2)
        similar_users_count = random.randint(2, k_neighbours)
        reason = random.choice(_MOCK_REASONS).format(k=similar_users_count)
        recommendations.append({
            **movie,
            "predicted_rating":    predicted_rating,
            "similar_users_count": similar_users_count,
            "reason":              reason,
        })

    # Sort by predicted rating descending (best first)
    recommendations.sort(key=lambda x: x["predicted_rating"], reverse=True)

    return {
        "data":   {"recommendations": recommendations},
        "error":  None,
        "source": "mock",
    }


def validate_user_id(user_id: int) -> dict:
    """
    Validate whether a User ID exists in the dataset.

    TODO: Replace mock with real call:
        GET /api/user/<user_id>/validate
        Returns { "valid": bool, "message": str }
    """
    url = f"{BACKEND_BASE_URL}/user/{user_id}/validate"
    data, error = _get(url)
    if data:
        return data

    # Mock fallback — accept any positive integer as valid
    if user_id > 0:
        return {"valid": True,  "message": "User found in dataset."}
    return {"valid": False, "message": "User ID must be a positive integer."}

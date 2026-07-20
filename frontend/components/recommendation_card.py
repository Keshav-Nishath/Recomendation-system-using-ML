"""
components/recommendation_card.py
----------------------------------
Renders a single movie recommendation card.

Card contents:
  - Movie poster (with placeholder fallback)
  - Movie title
  - Release year
  - Predicted rating badge
  - Number of similar users who liked it
  - Genre badges
  - Recommendation reason
  - Optional TMDB link

Hover effects (scale, shadow, poster zoom) are handled by style.css.
"""

import os
import streamlit as st
from utils.helpers import (
    format_rating,
    build_genre_badges_html,
    get_poster_url,
    get_recommendation_reason,
)
from config import COLORS


# ─── Resolve placeholder asset path once ─────────────────────────────────────
_CURRENT_DIR   = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIR  = os.path.dirname(_CURRENT_DIR)
_PLACEHOLDER   = os.path.join(_FRONTEND_DIR, "assets", "placeholder.jpg")


def render_recommendation_card(movie: dict) -> None:
    """
    Render a single recommendation card using HTML injected via st.markdown.

    Args:
        movie: dict containing movie data + recommendation metadata.
               Expected keys (all optional with fallbacks):
                 title, year, predicted_rating, similar_users_count,
                 genres, reason, poster_url, tmdb_url
    """
    title          = movie.get("title", "Unknown Title")
    year           = str(movie.get("year", "")) if movie.get("year") else ""
    predicted      = movie.get("predicted_rating", 0.0)
    similar_count  = movie.get("similar_users_count", 0)
    genres         = movie.get("genres", [])
    reason         = get_recommendation_reason(movie)
    tmdb_url       = movie.get("tmdb_url", "")

    rating_str    = format_rating(predicted, stars=True)
    genres_html   = build_genre_badges_html(genres)
    tmdb_html     = (
        f'<a class="rec-tmdb-link" href="{tmdb_url}" target="_blank">🔗 View on TMDB</a>'
        if tmdb_url else ""
    )

    # ── Poster image ──────────────────────────────────────────────────────────
    # Try URL first; fall back to local placeholder
    poster_url = movie.get("poster_url")
    if poster_url and poster_url.strip():
        poster_html = f'<img src="{poster_url}" alt="{title}" loading="lazy">'
    else:
        # Render the placeholder using st.image would require a column;
        # instead, show a styled fallback div with the movie emoji.
        poster_html = (
            '<div style="'
            "width:100%;height:100%;"
            "display:flex;align-items:center;justify-content:center;"
            "font-size:3.5rem;background:#1a1d2e;"
            '">🎬</div>'
        )

    # ── Assemble card HTML ────────────────────────────────────────────────────
    card_html = f"""
    <div class="rec-card">
        <div class="rec-poster">
            {poster_html}
        </div>
        <div class="rec-body">
            <p class="rec-title">{title}</p>
            <p class="rec-year">{year}</p>
            <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-top:0.15rem;">
                <span class="rec-rating-badge">{rating_str}</span>
                <span class="rec-similar-users">👥 {similar_count} similar user{'s' if similar_count != 1 else ''}</span>
            </div>
            <div class="rec-genres">
                {genres_html}
            </div>
            <p class="rec-reason">💡 {reason}</p>
            {f'<div style="margin-top:0.25rem;">{tmdb_html}</div>' if tmdb_html else ''}
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

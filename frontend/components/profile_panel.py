"""
components/profile_panel.py
----------------------------
Renders the Profile Context panel shown to the left of the recommendation
grid after recommendations are generated.
"""

import streamlit as st
from utils.helpers import format_rating, build_genre_badges_html, format_number
from config import COLORS


def render_profile_panel(profile: dict) -> None:
    """
    Render the user profile context panel.

    Args:
        profile: dict from api.client.get_user_profile()["data"]
                 Expected keys:
                   user_id      (int)
                   num_ratings  (int)
                   avg_rating   (float)
                   highly_rated (list of dicts with title, year, rating, genres)
    """
    user_id     = profile.get("user_id", "N/A")
    num_ratings = format_number(profile.get("num_ratings", 0))
    avg_rating  = format_rating(profile.get("avg_rating", 0))

    # ── Summary stats (pure inline styles — no CSS class dependency) ──────────
    st.markdown(
        f'<div style="'
        f'background:#202433;border:1px solid #30384A;border-radius:12px;'
        f'padding:1.25rem;margin-bottom:0.75rem;">'
        f'<p style="color:#C026FF;font-weight:700;font-size:1rem;margin-bottom:1rem;">👤 User Profile</p>'
        f'<div style="display:flex;justify-content:space-between;padding:0.4rem 0;border-bottom:1px solid #30384A;">'
        f'<span style="color:#B0B8CC;font-size:0.85rem;">User ID</span>'
        f'<span style="color:#C026FF;font-weight:600;">#{user_id}</span>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;padding:0.4rem 0;border-bottom:1px solid #30384A;">'
        f'<span style="color:#B0B8CC;font-size:0.85rem;">Movies Rated</span>'
        f'<span style="color:#FFFFFF;font-weight:600;">{num_ratings}</span>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;padding:0.4rem 0;">'
        f'<span style="color:#B0B8CC;font-size:0.85rem;">Average Rating</span>'
        f'<span style="color:#FFFFFF;font-weight:600;">{avg_rating}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Highly-rated movies ───────────────────────────────────────────────────
    st.markdown(
        '<p style="color:#B0B8CC;font-size:0.85rem;font-weight:600;'
        'text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">'
        '🌟 Highly Rated by User</p>',
        unsafe_allow_html=True,
    )

    highly_rated = profile.get("highly_rated", [])
    if not highly_rated:
        st.markdown(
            '<p style="font-size:0.8rem;color:#6B7280;">No highly rated movies on record.</p>',
            unsafe_allow_html=True,
        )
        return

    for movie in highly_rated:
        title      = movie.get("title", "Unknown")
        year_str   = str(movie.get("year", "")) if movie.get("year") else ""
        rating_str = format_rating(movie.get("rating", 0))
        genres_html = build_genre_badges_html(movie.get("genres", []))

        st.markdown(
            f'<div style="'
            f'background:#1a1d2e;border:1px solid #30384A;border-radius:8px;'
            f'padding:0.75rem;margin-bottom:0.5rem;">'
            f'<div style="color:#FFFFFF;font-weight:600;font-size:0.85rem;margin-bottom:0.25rem;">{title}</div>'
            f'<div style="color:#B0B8CC;font-size:0.78rem;margin-bottom:0.35rem;">'
            f'{year_str}&nbsp;·&nbsp;<span style="color:#34C759;font-weight:600;">{rating_str}</span>'
            f'</div>'
            f'<div>{genres_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

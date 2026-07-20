"""
components/profile_panel.py
----------------------------
Renders the Profile Context panel shown to the left of the recommendation
grid after recommendations are generated.

Displays:
  - User ID
  - Number of movies rated
  - Average user rating
  - List of highly-rated movies (with title, year, rating, genres)
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
    st.markdown(
        """
        <div class="profile-panel">
            <h3>👤 User Profile</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Summary stats ─────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="profile-panel" style="margin-top:-0.6rem;">
            <h3 style="margin-bottom:0.75rem;">👤 User Profile</h3>

            <div class="profile-stat-row">
                <span class="profile-stat-label">User ID</span>
                <span class="profile-stat-value" style="color:#C026FF;">#{profile.get('user_id', 'N/A')}</span>
            </div>
            <div class="profile-stat-row">
                <span class="profile-stat-label">Movies Rated</span>
                <span class="profile-stat-value">{format_number(profile.get('num_ratings', 0))}</span>
            </div>
            <div class="profile-stat-row" style="border-bottom:none;">
                <span class="profile-stat-label">Average Rating</span>
                <span class="profile-stat-value">{format_rating(profile.get('avg_rating', 0))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Highly-rated movies section ───────────────────────────────────────────
    st.markdown(
        '<p class="section-heading" style="margin-bottom:0.6rem;">🌟 Highly Rated by User</p>',
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
        genres_html = build_genre_badges_html(movie.get("genres", []))
        rating_str  = format_rating(movie.get("rating", 0))
        year_str    = str(movie.get("year", "")) if movie.get("year") else ""

        st.markdown(
            f"""
            <div class="highly-rated-card">
                <div class="highly-rated-title">{movie.get('title', 'Unknown')}</div>
                <div class="highly-rated-meta" style="margin-bottom:0.3rem;">
                    {year_str}
                    &nbsp;·&nbsp;
                    <span style="color:#34C759;font-weight:600;">{rating_str}</span>
                </div>
                <div>{genres_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

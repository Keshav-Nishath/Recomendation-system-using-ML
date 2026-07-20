"""
components/recommendation_grid.py
-----------------------------------
Renders the recommendation results section.

Layout:
  ┌────────────────────────────────────────────────────────┐
  │  [Profile Context — 35%]  │  [Movie Grid — 65%]        │
  └────────────────────────────────────────────────────────┘

The grid renders 3 cards per row on desktop (handled by Streamlit columns).
"""

import streamlit as st
from components.profile_panel import render_profile_panel
from components.recommendation_card import render_recommendation_card
from config import CARDS_PER_ROW


def _render_results_header(count: int) -> None:
    """Render the 'Recommended Movies' section header with count badge."""
    st.markdown(
        f"""
        <div class="results-header">
            <h2>🎬 Recommended Movies</h2>
            <span class="results-badge">{count} results</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_movie_grid(recommendations: list[dict]) -> None:
    """
    Display recommendation cards in a 3-column responsive grid.

    Streamlit does not natively support CSS grid for card-level layout,
    so we use st.columns() with CARDS_PER_ROW columns and fill them row
    by row.
    """
    if not recommendations:
        return

    # Chunk recommendations into rows of CARDS_PER_ROW
    for row_start in range(0, len(recommendations), CARDS_PER_ROW):
        row_movies = recommendations[row_start : row_start + CARDS_PER_ROW]
        cols = st.columns(CARDS_PER_ROW, gap="medium")
        for col, movie in zip(cols, row_movies):
            with col:
                render_recommendation_card(movie)
        st.markdown("<br>", unsafe_allow_html=True)


def render_recommendation_grid(recommendations: list[dict], profile: dict) -> None:
    """
    Render the full results view: Profile Context (35%) + Movie Grid (65%).

    Args:
        recommendations: list of recommendation dicts from the API.
        profile:         user profile dict from the API.
    """
    if not recommendations:
        return

    _render_results_header(len(recommendations))

    # ── Two-column split: profile (35%) | grid (65%) ──────────────────────────
    profile_col, grid_col = st.columns([35, 65], gap="large")

    with profile_col:
        render_profile_panel(profile)

    with grid_col:
        _render_movie_grid(recommendations)

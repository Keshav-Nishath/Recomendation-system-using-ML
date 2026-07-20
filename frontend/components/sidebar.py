"""
components/sidebar.py
---------------------
Renders the CineMatch sidebar.

Contents:
  - Logo / branding
  - System status cards
  - Dataset statistics (metrics)

Data is fetched from the API client; results are cached in session_state
so the sidebar doesn't re-fetch on every Streamlit rerun.
"""

import streamlit as st
from api.client import get_backend_status, get_dataset_stats
from utils.helpers import format_number
from config import (
    APP_NAME,
    APP_TAGLINE,
    SYSTEM_STATUS_ITEMS,
    SessionKeys,
    COLORS,
)


# ── Private helpers ───────────────────────────────────────────────────────────

def _render_logo() -> None:
    """Display the CineMatch logo and tagline at the top of the sidebar."""
    st.markdown(
        f"""
        <div class="sidebar-logo">
            <span class="logo-icon">🎬</span>
            <span class="logo-title">{APP_NAME}</span>
            <span class="logo-subtitle">{APP_TAGLINE}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_divider() -> None:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


def _render_system_status(status_data: dict) -> None:
    """
    Display four system-status cards.
    Each maps to a key returned by the backend health endpoint.
    TODO: backend key mapping comes from GET /api/health response.
    """
    st.markdown('<p class="section-heading">🔧 System Status</p>', unsafe_allow_html=True)

    status_keys = {
        SYSTEM_STATUS_ITEMS[0]: status_data.get("recommendation_engine", True),
        SYSTEM_STATUS_ITEMS[1]: status_data.get("similarity_matrix",     True),
        SYSTEM_STATUS_ITEMS[2]: status_data.get("dataset",               True),
        SYSTEM_STATUS_ITEMS[3]: status_data.get("system",                True),
    }

    for label, is_ok in status_keys.items():
        if is_ok:
            st.markdown(
                f"""
                <div class="status-card">
                    <div class="status-dot"></div>
                    <span>✓ {label}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Offline / degraded style
            st.markdown(
                f"""
                <div class="status-card" style="
                    background: rgba(255,59,48,0.08);
                    border-color: rgba(255,59,48,0.25);
                    color: #FF3B30;">
                    <div class="status-dot" style="background:#FF3B30;box-shadow:0 0 6px #FF3B30;"></div>
                    <span>✗ {label}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_dataset_stats(stats_data: dict) -> None:
    """
    Display dataset statistics as Streamlit metric widgets.
    TODO: values come from GET /api/stats response.
    """
    st.markdown('<p class="section-heading">📊 Dataset Statistics</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Active Users",
            value=format_number(stats_data.get("active_users", 0)),
        )
    with col2:
        st.metric(
            label="Movies",
            value=format_number(stats_data.get("movies", 0)),
        )

    col3, col4 = st.columns(2)
    with col3:
        st.metric(
            label="Total Ratings",
            value=format_number(stats_data.get("ratings", 0)),
        )
    with col4:
        st.metric(
            label="Avg Rating",
            value=f"{stats_data.get('avg_rating', 0):.2f} ⭐",
        )


# ── Public render function ────────────────────────────────────────────────────

def render_sidebar() -> None:
    """
    Main entry point. Renders the complete sidebar inside st.sidebar context.

    Call this once from app.py.
    """
    with st.sidebar:
        _render_logo()
        _render_divider()

        # ── Fetch / cache system status ──────────────────────────────────────
        if st.session_state.get(SessionKeys.BACKEND_STATUS) is None:
            result = get_backend_status()
            st.session_state[SessionKeys.BACKEND_STATUS] = result.get("data", {})

        _render_system_status(st.session_state[SessionKeys.BACKEND_STATUS])
        _render_divider()

        # ── Fetch / cache dataset statistics ─────────────────────────────────
        if st.session_state.get(SessionKeys.SIDEBAR_STATS) is None:
            result = get_dataset_stats()
            st.session_state[SessionKeys.SIDEBAR_STATS] = result.get("data", {})

        _render_dataset_stats(st.session_state[SessionKeys.SIDEBAR_STATS])
        _render_divider()

        # ── Footer note ───────────────────────────────────────────────────────
        st.markdown(
            '<p style="font-size:0.68rem;color:#6B7280;text-align:center;margin-top:0.5rem;">'
            "Collaborative Filtering · MovieLens Dataset"
            "</p>",
            unsafe_allow_html=True,
        )

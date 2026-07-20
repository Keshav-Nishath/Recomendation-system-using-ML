"""
components/header.py
--------------------
Renders the centered main-content header for CineMatch.

Displays:
  - App icon
  - Large gradient title
  - Tagline
  - Description subtitle
"""

import streamlit as st
from config import APP_NAME, APP_TAGLINE, APP_DESCRIPTION


def render_header() -> None:
    """Render the CineMatch page header, centered in the main content area."""
    st.markdown(
        f"""
        <div class="main-header">
            <span class="header-icon">🎬</span>
            <h1>{APP_NAME}</h1>
            <p class="header-tagline">{APP_TAGLINE}</p>
            <p class="header-description">{APP_DESCRIPTION}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

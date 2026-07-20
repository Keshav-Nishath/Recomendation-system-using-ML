"""
app.py
------
CineMatch — AI-Powered Collaborative Movie Recommendation System

Entry point for `streamlit run app.py`.

Responsibilities:
  1. Configure the Streamlit page (wide layout, icon, title)
  2. Load custom CSS
  3. Initialise session_state defaults
  4. Render sidebar
  5. Render header
  6. Render controls and handle Generate button click
  7. Show loading spinner while fetching data
  8. Display profile context + recommendation grid
  9. Handle notifications (success / warning / error)
  10. Show empty state when no recommendations exist

All presentation logic lives in the components/ directory.
All API communication lives in api/client.py.
"""

import sys
import os

# ── Ensure the frontend/ directory is on sys.path so imports resolve cleanly
# when running:  streamlit run app.py   from inside frontend/
# or:            streamlit run frontend/app.py  from the project root.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import time
import streamlit as st

# ─── Page Config (must be the first Streamlit call) ───────────────────────────
st.set_page_config(
    page_title="CineMatch — Movie Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "CineMatch v1.0 — AI-Powered Collaborative Filtering",
    },
)

# ─── Local imports (after path is set up) ────────────────────────────────────
from config import SessionKeys, LOADING_MESSAGES
from utils.helpers import init_session_state, load_css, should_warn_few_ratings
from components.sidebar import render_sidebar
from components.header import render_header
from components.controls import render_controls
from components.recommendation_grid import render_recommendation_grid
from api.client import get_recommendations, get_user_profile, validate_user_id


# ─── CSS ─────────────────────────────────────────────────────────────────────

def _load_styles() -> None:
    """Inject the custom stylesheet and any extra inline overrides."""
    css_path = os.path.join(_THIS_DIR, "styles", "style.css")
    load_css(st, css_path)

    # Extra viewport meta for better mobile rendering
    st.markdown(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        unsafe_allow_html=True,
    )


# ─── Empty State ─────────────────────────────────────────────────────────────

def _render_empty_state() -> None:
    """Display the empty state before any recommendations are generated."""
    st.markdown(
        """
        <div class="empty-state">
            <span class="empty-icon">🎬</span>
            <h3>No recommendations generated yet.</h3>
            <p>Enter a User ID, adjust the controls above, then click
               <strong>Generate Recommendations</strong> to begin.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Recommendation Flow ──────────────────────────────────────────────────────

def _fetch_and_store_recommendations(user_id: int, rec_count: int, k_value: int) -> None:
    """
    Fetch user profile + recommendations from the API client,
    store results in session_state, and display a loading spinner.

    TODO: When Flask backend is live, api/client.py functions will
          send real HTTP requests instead of returning mock data.
    """
    loading_messages = LOADING_MESSAGES

    with st.spinner(loading_messages[0]):
        # Step 1 — Validate user exists
        validation = validate_user_id(user_id)
        if not validation.get("valid", True):
            st.session_state[SessionKeys.RECOMMENDATIONS] = None
            st.session_state[SessionKeys.PROFILE_CONTEXT] = None
            st.error(f"❌ {validation.get('message', 'Invalid User ID.')}")
            return

    with st.spinner(loading_messages[1]):
        # Step 2 — Fetch user profile
        profile_result = get_user_profile(user_id)
        time.sleep(0.4)   # brief pause so the spinner is visible

    with st.spinner(loading_messages[2]):
        # Step 3 — Fetch recommendations
        rec_result = get_recommendations(
            user_id=user_id,
            n_recommendations=rec_count,
            k_neighbours=k_value,
        )
        time.sleep(0.4)

    with st.spinner(loading_messages[3]):
        time.sleep(0.3)

    # ── Handle errors ─────────────────────────────────────────────────────────
    if rec_result.get("error"):
        st.error(f"❌ Recommendation generation failed: {rec_result['error']}")
        st.session_state[SessionKeys.RECOMMENDATIONS] = None
        st.session_state[SessionKeys.PROFILE_CONTEXT] = None
        return

    if profile_result.get("error"):
        st.warning(f"⚠️ Could not load profile: {profile_result['error']}")

    # ── Store results in session_state ────────────────────────────────────────
    recommendations = rec_result["data"].get("recommendations", [])
    profile         = profile_result.get("data", {})

    st.session_state[SessionKeys.RECOMMENDATIONS] = recommendations
    st.session_state[SessionKeys.PROFILE_CONTEXT]  = profile
    st.session_state[SessionKeys.USER_ID]          = user_id

    # ── Success notification ──────────────────────────────────────────────────
    if recommendations:
        st.success(
            f"✅ Recommendations Generated Successfully! "
            f"Found {len(recommendations)} movies for User #{user_id}."
        )

        # Warning: user has rated very few movies
        if should_warn_few_ratings(profile, threshold=20):
            st.warning(
                "⚠️ This user has rated very few movies. "
                "Recommendations may be less accurate."
            )
    else:
        st.warning("⚠️ No recommendations could be generated for this user.")


# ─── Main App ─────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Application entry point.
    Orchestrates all component renders and the recommendation workflow.
    """
    # 1 ── Bootstrap ──────────────────────────────────────────────────────────
    _load_styles()
    init_session_state(st)

    # 2 ── Sidebar (always visible) ────────────────────────────────────────────
    render_sidebar()

    # 3 ── Main content ────────────────────────────────────────────────────────
    render_header()

    # Thin separator
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 4 ── Controls ────────────────────────────────────────────────────────────
    controls = render_controls()

    # 5 ── Handle Generate button click ───────────────────────────────────────
    if controls["generate_clicked"]:
        if controls["error"]:
            # Show input validation error immediately
            st.error(f"❌ {controls['error']}")
        elif controls["user_id"] is None:
            st.error("❌ Please enter a User ID.")
        else:
            # Clear any stale results so the loading spinners show cleanly
            st.session_state[SessionKeys.RECOMMENDATIONS] = None
            st.session_state[SessionKeys.PROFILE_CONTEXT] = None

            _fetch_and_store_recommendations(
                user_id   = controls["user_id"],
                rec_count = controls["rec_count"],
                k_value   = controls["k_value"],
            )

    # 6 ── Results or Empty State ──────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    recommendations = st.session_state.get(SessionKeys.RECOMMENDATIONS)
    profile         = st.session_state.get(SessionKeys.PROFILE_CONTEXT)

    if recommendations:
        render_recommendation_grid(
            recommendations = recommendations,
            profile         = profile or {},
        )
    else:
        _render_empty_state()


# ─── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

"""
components/controls.py
----------------------
Renders all interactive controls for generating recommendations:

  1. User mode selection (Existing User / New User — Coming Soon)
  2. User ID text input with sample IDs
  3. Number of Recommendations slider
  4. Number of Similar Users (K) slider
  5. Generate Recommendations button

Returns a dict describing the current control state so app.py can
act on the Generate button click.
"""

import streamlit as st
from config import (
    SAMPLE_USER_IDS,
    RECOMMENDATION_COUNT_MIN,
    RECOMMENDATION_COUNT_MAX,
    RECOMMENDATION_COUNT_DEFAULT,
    K_NEIGHBOURS_MIN,
    K_NEIGHBOURS_MAX,
    K_NEIGHBOURS_DEFAULT,
    SessionKeys,
    COLORS,
)
from utils.helpers import validate_user_id_input


def render_controls() -> dict:
    """
    Render all recommendation controls.

    Returns:
        {
            "generate_clicked": bool,
            "user_id":          int | None,
            "rec_count":        int,
            "k_value":          int,
            "error":            str | None,
        }
    """
    result = {
        "generate_clicked": False,
        "user_id":          None,
        "rec_count":        st.session_state.get(SessionKeys.REC_COUNT, RECOMMENDATION_COUNT_DEFAULT),
        "k_value":          st.session_state.get(SessionKeys.K_VALUE, K_NEIGHBOURS_DEFAULT),
        "error":            None,
    }

    # ── Section heading ───────────────────────────────────────────────────────
    st.markdown(
        '<p class="section-heading" style="margin-top:0.5rem;">🎛️ Recommendation Settings</p>',
        unsafe_allow_html=True,
    )

    # ── Control panel container ───────────────────────────────────────────────
    with st.container():
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)

        # ── 1. User Mode Selection ────────────────────────────────────────────
        st.markdown('<p class="control-label">User Mode</p>', unsafe_allow_html=True)
        user_mode = st.radio(
            label="user_mode_radio",
            options=["Existing User", "New User (Coming Soon)"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            key=SessionKeys.USER_MODE,
        )

        if user_mode == "New User (Coming Soon)":
            st.info(
                "ℹ️ Cold-start recommendations are not available in the current version. "
                "Please select **Existing User** to continue.",
                icon=None,
            )
            st.markdown("</div>", unsafe_allow_html=True)
            return result

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 2. User ID Input ──────────────────────────────────────────────────
        col_input, col_space = st.columns([1, 1])
        with col_input:
            st.markdown('<p class="control-label">User ID</p>', unsafe_allow_html=True)
            raw_uid = st.text_input(
                label="user_id_input",
                placeholder="e.g. 4",
                value=str(st.session_state.get(SessionKeys.USER_ID, ""))
                      if st.session_state.get(SessionKeys.USER_ID) else "",
                label_visibility="collapsed",
                key="_raw_user_id_input",
            )

            # Sample IDs
            sample_badges = "".join(
                f'<span class="sample-id-badge">{uid}</span>'
                for uid in SAMPLE_USER_IDS
            )
            st.markdown(
                f'<div style="margin-top:0.35rem;">'
                f'<span style="font-size:0.7rem;color:#6B7280;margin-right:6px;">Sample IDs:</span>'
                f'<div class="sample-ids">{sample_badges}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

        # Validate input immediately (but only show error if generate is clicked)
        uid, uid_error = validate_user_id_input(raw_uid)
        result["user_id"] = uid
        result["error"]   = uid_error

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 3. Recommendation Count Slider ────────────────────────────────────
        st.markdown('<p class="control-label">Number of Recommendations</p>', unsafe_allow_html=True)
        rec_count = st.slider(
            label="rec_count_slider",
            min_value=RECOMMENDATION_COUNT_MIN,
            max_value=RECOMMENDATION_COUNT_MAX,
            value=st.session_state.get(SessionKeys.REC_COUNT, RECOMMENDATION_COUNT_DEFAULT),
            step=1,
            label_visibility="collapsed",
            key="_rec_count_slider",
        )
        st.session_state[SessionKeys.REC_COUNT] = rec_count
        result["rec_count"] = rec_count

        st.markdown(
            f'<p style="font-size:0.72rem;color:#6B7280;margin-top:-0.4rem;">'
            f'Will return <strong style="color:#C026FF;">{rec_count}</strong> movie recommendations.'
            f"</p>",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 4. K-Neighbours Slider ────────────────────────────────────────────
        st.markdown('<p class="control-label">Number of Similar Users (K)</p>', unsafe_allow_html=True)
        k_value = st.slider(
            label="k_slider",
            min_value=K_NEIGHBOURS_MIN,
            max_value=K_NEIGHBOURS_MAX,
            value=st.session_state.get(SessionKeys.K_VALUE, K_NEIGHBOURS_DEFAULT),
            step=1,
            label_visibility="collapsed",
            key="_k_slider",
        )
        st.session_state[SessionKeys.K_VALUE] = k_value
        result["k_value"] = k_value

        st.markdown(
            f'<p style="font-size:0.72rem;color:#6B7280;margin-top:-0.4rem;">'
            f'Uses <strong style="color:#4DA3FF;">{k_value}</strong> nearest neighbour(s) for scoring.'
            f"</p>",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 5. Generate Button ────────────────────────────────────────────────
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            generate_clicked = st.button(
                label="🎬 Generate Recommendations",
                use_container_width=True,
                key="generate_btn",
            )

        result["generate_clicked"] = generate_clicked

        st.markdown("</div>", unsafe_allow_html=True)  # close .control-panel

    return result

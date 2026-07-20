"""
utils/helpers.py
----------------
Utility / helper functions for CineMatch.
Handles formatting, data processing, and shared UI logic.
"""

from config import GENRE_COLORS, COLORS


# ─── Number Formatting ────────────────────────────────────────────────────────

def format_number(value: int | float) -> str:
    """
    Format a large number with comma separators.
    e.g. 1000209 → "1,000,209"
    """
    if isinstance(value, float):
        return f"{value:,.2f}"
    return f"{int(value):,}"


def format_rating(rating: float, stars: bool = True) -> str:
    """
    Format a rating value.
    e.g. 4.8 → "⭐ 4.8"
    """
    formatted = f"{rating:.1f}"
    return f"⭐ {formatted}" if stars else formatted


def format_year(year: int | str | None) -> str:
    """Return the year as a 4-digit string, or empty string if None."""
    if year is None:
        return ""
    return str(year)


# ─── Genre Helpers ────────────────────────────────────────────────────────────

def get_genre_color(genre: str) -> str:
    """Return the hex color for a genre badge, with a default fallback."""
    return GENRE_COLORS.get(genre, GENRE_COLORS["default"])


def build_genre_badges_html(genres: list[str]) -> str:
    """
    Render a list of genre strings as inline HTML badge spans.
    Used inside st.markdown(..., unsafe_allow_html=True).
    """
    if not genres:
        return ""
    badges = []
    for genre in genres:
        color = get_genre_color(genre)
        badge = (
            f'<span style="'
            f'background-color:{color}22;'
            f'color:{color};'
            f'border:1px solid {color}55;'
            f'border-radius:12px;'
            f'padding:2px 10px;'
            f'font-size:0.72rem;'
            f'font-weight:600;'
            f'margin-right:4px;'
            f'display:inline-block;'
            f'margin-bottom:4px;'
            f'">{genre}</span>'
        )
        badges.append(badge)
    return " ".join(badges)


# ─── Rating Star Display ──────────────────────────────────────────────────────

def rating_to_stars(rating: float, max_rating: float = 5.0) -> str:
    """
    Convert a numeric rating to a visual star string.
    e.g. 4.0 / 5.0 → "★★★★☆"
    """
    filled  = round(rating)
    empty   = int(max_rating) - filled
    return "★" * filled + "☆" * empty


# ─── Session State Helpers ────────────────────────────────────────────────────

def init_session_state(st) -> None:
    """
    Initialise all required Streamlit session_state keys with default values
    if they are not already set. Call this at the top of app.py.
    """
    from config import (
        SessionKeys,
        RECOMMENDATION_COUNT_DEFAULT,
        K_NEIGHBOURS_DEFAULT,
    )
    defaults = {
        SessionKeys.USER_ID:         None,
        SessionKeys.REC_COUNT:       RECOMMENDATION_COUNT_DEFAULT,
        SessionKeys.K_VALUE:         K_NEIGHBOURS_DEFAULT,
        SessionKeys.RECOMMENDATIONS: None,
        SessionKeys.PROFILE_CONTEXT: None,
        SessionKeys.SIDEBAR_STATS:   None,
        SessionKeys.BACKEND_STATUS:  None,
        SessionKeys.USER_MODE:       "Existing User",
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


# ─── Data Validation ─────────────────────────────────────────────────────────

def validate_user_id_input(raw_input: str) -> tuple[int | None, str | None]:
    """
    Validate and parse a raw user-ID string from the text input.

    Returns:
        (user_id, None)        — valid integer
        (None, error_message)  — invalid input
    """
    if not raw_input or not raw_input.strip():
        return None, "Please enter a User ID."
    try:
        uid = int(raw_input.strip())
        if uid <= 0:
            return None, "User ID must be a positive integer."
        return uid, None
    except ValueError:
        return None, f"'{raw_input}' is not a valid integer User ID."


# ─── Recommendation Reason ───────────────────────────────────────────────────

def get_recommendation_reason(movie: dict) -> str:
    """
    Extract or generate a human-readable recommendation reason from a movie dict.
    Falls back to a generic message if no reason is stored.
    """
    return movie.get("reason", "Recommended based on collaborative filtering.")


# ─── Poster URL ──────────────────────────────────────────────────────────────

def get_poster_url(movie: dict, placeholder_path: str) -> str:
    """
    Return the poster URL if available, otherwise return the local placeholder path.
    """
    url = movie.get("poster_url")
    if url and url.strip():
        return url
    return placeholder_path


# ─── Notification Helpers ─────────────────────────────────────────────────────

def should_warn_few_ratings(profile: dict, threshold: int = 20) -> bool:
    """
    Return True if the user has rated fewer movies than the threshold,
    which may reduce recommendation accuracy.
    """
    return profile.get("num_ratings", 0) < threshold


# ─── CSS Load Helper ──────────────────────────────────────────────────────────

def load_css(st, css_path: str) -> None:
    """
    Read a CSS file and inject it into the Streamlit page via st.markdown.
    """
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Silently skip if CSS file not found; inline styles will still apply
        pass

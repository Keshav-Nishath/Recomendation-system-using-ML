"""
config.py
---------
Application-wide configuration constants for CineMatch.
All colors, endpoints, defaults, and UI settings are defined here.
"""

# ─── Application Meta ────────────────────────────────────────────────────────
APP_NAME = "CineMatch"
APP_TAGLINE = "AI-Powered Collaborative Movie Recommendation System"
APP_DESCRIPTION = "Discover movies loved by users with tastes similar to yours."
APP_VERSION = "1.0.0"

# ─── Flask Backend Base URL ───────────────────────────────────────────────────
# TODO: Replace with actual Flask backend URL when backend is available
BACKEND_BASE_URL = "http://localhost:5000"

# ─── API Endpoints ────────────────────────────────────────────────────────────
# Matches the Flask backend routes exactly (no /api prefix)
API_ENDPOINTS = {
    "health":       f"{BACKEND_BASE_URL}/health",
    "stats":        f"{BACKEND_BASE_URL}/stats",
    "recommend":    f"{BACKEND_BASE_URL}/recommend",
}

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_primary":    "#0F1117",
    "bg_sidebar":    "#1B1E27",
    "bg_card":       "#202433",
    "bg_border":     "#30384A",

    # Accents
    "accent_purple": "#C026FF",
    "accent_blue":   "#4DA3FF",
    "accent_green":  "#34C759",
    "accent_orange": "#FF9500",
    "accent_red":    "#FF3B30",

    # Text
    "text_primary":  "#FFFFFF",
    "text_secondary":"#B0B8CC",
    "text_muted":    "#6B7280",
}

# ─── Recommendation Controls Defaults ────────────────────────────────────────
RECOMMENDATION_COUNT_MIN     = 5
RECOMMENDATION_COUNT_MAX     = 20
RECOMMENDATION_COUNT_DEFAULT = 10

K_NEIGHBOURS_MIN     = 1
K_NEIGHBOURS_MAX     = 10
K_NEIGHBOURS_DEFAULT = 6

# ─── Sample User IDs (shown below the input field) ───────────────────────────
SAMPLE_USER_IDS = [4, 11, 12, 13, 14, 15, 17, 20]

# ─── Genre Badge Colors ───────────────────────────────────────────────────────
# Maps genre names to CSS background colors
GENRE_COLORS = {
    "Action":          "#FF3B30",
    "Adventure":       "#FF9500",
    "Animation":       "#FFD60A",
    "Children's":      "#34C759",
    "Comedy":          "#30D158",
    "Crime":           "#FF453A",
    "Documentary":     "#636366",
    "Drama":           "#4DA3FF",
    "Fantasy":         "#BF5AF2",
    "Film-Noir":       "#48484A",
    "Horror":          "#FF375F",
    "Musical":         "#FF9F0A",
    "Mystery":         "#5E5CE6",
    "Romance":         "#FF2D55",
    "Sci-Fi":          "#64D2FF",
    "Science Fiction": "#64D2FF",
    "Thriller":        "#FF6B35",
    "War":             "#8E8E93",
    "Western":         "#A2845E",
    "default":         "#4DA3FF",
}

# ─── Loading Messages ─────────────────────────────────────────────────────────
LOADING_MESSAGES = [
    "Finding users with similar preferences...",
    "Calculating recommendation scores...",
    "Ranking movies...",
    "Preparing recommendations...",
]

# ─── System Status Labels ─────────────────────────────────────────────────────
SYSTEM_STATUS_ITEMS = [
    "Recommendation Engine Ready",
    "Similarity Matrix Loaded",
    "Dataset Loaded",
    "System Online",
]

# ─── Session State Keys ───────────────────────────────────────────────────────
class SessionKeys:
    USER_ID           = "user_id"
    REC_COUNT         = "rec_count"
    K_VALUE           = "k_value"
    RECOMMENDATIONS   = "recommendations"
    PROFILE_CONTEXT   = "profile_context"
    SIDEBAR_STATS     = "sidebar_stats"
    BACKEND_STATUS    = "backend_status"
    USER_MODE         = "user_mode"

# ─── UI Settings ──────────────────────────────────────────────────────────────
MAX_CONTENT_WIDTH   = "1200px"
CARDS_PER_ROW       = 3          # desktop grid columns
POSTER_ASPECT_RATIO = (2, 3)     # width : height ratio for movie posters

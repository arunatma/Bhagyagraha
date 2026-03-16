"""
themes.py — Color theme definitions for Bhagyagraha.

Each theme is a dict of semantic color tokens used by the Streamlit CSS,
HTML report, and PDF report.  The app stores the active theme name in
st.session_state and passes the corresponding dict to the generators.
"""

THEMES = {
    "Teal & Charcoal": {
        "accent": "#14B8A6",
        "accent_hover": "#0e9688",
        "accent_rgb": "20,184,166",
        "sidebar_bg": "#2D2D2D",
        "sidebar_text": "#E5E5E5",
        "sidebar_input_bg": "#3A3A3A",
        "sidebar_divider": "#4A4A4A",
        "header_bg": "#2D2D2D",
        "header_text": "#E5E5E5",
        "body_bg": "#FFFFFF",
        "body_text": "#2D2D2D",
        "muted_text": "#555555",
        "table_border": "#E4E4E7",
        "table_alt_row": "#F7F7F7",
        "table_header_bg": "#F7F7F7",
        "retro_color": "#0e9688",
        "chart_border": "#444",
    },
    "Indigo & Ivory": {
        "accent": "#6366F1",
        "accent_hover": "#4F46E5",
        "accent_rgb": "99,102,241",
        "sidebar_bg": "#1E1B4B",
        "sidebar_text": "#E0E7FF",
        "sidebar_input_bg": "#312E81",
        "sidebar_divider": "#4338CA",
        "header_bg": "#1E1B4B",
        "header_text": "#E0E7FF",
        "body_bg": "#FFFFF8",
        "body_text": "#1E1B4B",
        "muted_text": "#6B7280",
        "table_border": "#E5E7EB",
        "table_alt_row": "#F5F3FF",
        "table_header_bg": "#EEF2FF",
        "retro_color": "#4F46E5",
        "chart_border": "#4338CA",
    },
    "Rose Gold & Slate": {
        "accent": "#E11D48",
        "accent_hover": "#BE123C",
        "accent_rgb": "225,29,72",
        "sidebar_bg": "#1E293B",
        "sidebar_text": "#E2E8F0",
        "sidebar_input_bg": "#334155",
        "sidebar_divider": "#475569",
        "header_bg": "#1E293B",
        "header_text": "#E2E8F0",
        "body_bg": "#FFFFFF",
        "body_text": "#1E293B",
        "muted_text": "#64748B",
        "table_border": "#E2E8F0",
        "table_alt_row": "#FFF1F2",
        "table_header_bg": "#FFE4E6",
        "retro_color": "#BE123C",
        "chart_border": "#94A3B8",
    },
    "Forest & Stone": {
        "accent": "#059669",
        "accent_hover": "#047857",
        "accent_rgb": "5,150,105",
        "sidebar_bg": "#1C1917",
        "sidebar_text": "#E7E5E4",
        "sidebar_input_bg": "#292524",
        "sidebar_divider": "#44403C",
        "header_bg": "#1C1917",
        "header_text": "#E7E5E4",
        "body_bg": "#FAFAF9",
        "body_text": "#1C1917",
        "muted_text": "#78716C",
        "table_border": "#D6D3D1",
        "table_alt_row": "#F5F5F4",
        "table_header_bg": "#ECFDF5",
        "retro_color": "#047857",
        "chart_border": "#57534E",
    },
}

THEME_NAMES = list(THEMES.keys())


def get_theme(name):
    """Return theme dict by name, defaulting to the first theme."""
    return THEMES.get(name, THEMES[THEME_NAMES[0]])


def build_streamlit_css(t):
    """Return the full <style> block for Streamlit, parameterized by theme dict *t*."""
    return f"""<style>
/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {t["sidebar_bg"]} !important;
    border-right: 2px solid {t["accent"]} !important;
}}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{
    color: {t["sidebar_text"]} !important;
}}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: {t["accent"]} !important;
}}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {{
    background-color: {t["sidebar_input_bg"]} !important;
    border: 1px solid {t["accent"]} !important;
    color: {t["sidebar_text"]} !important;
    border-radius: 6px !important;
}}
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stDateInput > div > div,
section[data-testid="stSidebar"] .stTimeInput > div > div {{
    background-color: {t["sidebar_input_bg"]} !important;
    border: 1px solid {t["accent"]} !important;
    color: {t["sidebar_text"]} !important;
    border-radius: 6px !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: {t["sidebar_divider"]} !important;
    margin: 0.6rem 0 !important;
}}
.sb-section {{
    background: rgba({t["accent_rgb"]},0.10);
    border-left: 3px solid {t["accent"]};
    border-radius: 0 6px 6px 0;
    padding: 8px 10px 8px 12px;
    margin: 8px 0 4px 0;
}}
.sb-section-title {{
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {t["accent"]} !important;
}}

/* ── Main area — override Streamlit dark mode on every container ── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stBottom"],
.main {{
    background-color: {t["body_bg"]} !important;
    color: {t["body_text"]} !important;
}}
.main .block-container {{
    background-color: {t["body_bg"]} !important;
    padding-top: 1rem !important;
}}
.main .stMarkdown,
.main p, .main span, .main label, .main div {{
    color: {t["body_text"]} !important;
}}

/* ── Page header banner ── */
.bhagya-header {{
    background: {t["header_bg"]};
    color: {t["header_text"]};
    padding: 1.2rem 2rem;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 1.2rem;
    border: 1px solid {t["table_border"]};
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}}
.bhagya-header h1 {{
    font-size: 1.8rem;
    letter-spacing: 6px;
    margin: 0 0 0.2rem 0;
    color: {t["accent"]};
}}
.bhagya-header .subhead {{
    font-size: 0.85rem;
    color: {t["header_text"]};
    letter-spacing: 2px;
}}

/* ── Section headings ── */
.section-head {{
    font-size: 1rem;
    font-weight: 700;
    color: {t["accent"]};
    border-bottom: 2px solid {t["accent"]};
    padding-bottom: 0.3rem;
    margin: 1.2rem 0 0.7rem 0;
    letter-spacing: 1px;
    text-transform: uppercase;
}}

/* ── Primary button ── */
.stButton > button[kind="primary"] {{
    background: {t["accent"]} !important;
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    box-shadow: 0 2px 6px rgba({t["accent_rgb"]},0.30) !important;
    transition: all 0.2s !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: {t["accent_hover"]} !important;
    box-shadow: 0 4px 12px rgba({t["accent_rgb"]},0.45) !important;
    transform: translateY(-1px) !important;
}}

/* ── Download buttons ── */
.stDownloadButton > button {{
    background: {t["table_alt_row"]} !important;
    border: 1px solid {t["accent"]} !important;
    color: {t["accent"]} !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}}
.stDownloadButton > button:hover {{
    background: {t["accent"]} !important;
    color: #FFFFFF !important;
}}

/* ── Dataframes ── */
.stDataFrame {{
    border: 1px solid {t["table_border"]} !important;
    border-radius: 8px !important;
}}

/* ── Divider ── */
hr {{ border-color: {t["table_border"]} !important; }}
</style>"""

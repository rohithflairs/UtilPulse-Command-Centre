"""
UtilPulse Command Centre — Minimal Editorial Black & White Design System
========================================================================
Implements a Swiss-style, typography-first, high-contrast black & white aesthetic.
One accent color defined via --accent. No gradients, no glassmorphism, no box cards, no emojis.
"""

import streamlit as st

# Single source of truth for the accent color
ACCENT_COLOR = "#00E0B8"


def apply_custom_css():
    """Injects minimal, editorial global CSS styling into the Streamlit application."""
    css = f"""
    <style>
    /* -------------------------------------------------------------------------
       1. Typography & Google Fonts
       ------------------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {{
        --bg-canvas: #0A0A0A;
        --bg-surface: #111111;
        --text-primary: #F5F5F5;
        --text-secondary: #8A8A8A;
        --text-muted: #555555;
        --border-hairline: #222222;
        --border-subtle: #2A2A2A;
        --accent: {ACCENT_COLOR};
        --font-display: 'Space Grotesk', -apple-system, sans-serif;
        --font-body: 'Inter', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }}

    /* -------------------------------------------------------------------------
       2. Streamlit Chrome Cleanup & Canvas Reset
       ------------------------------------------------------------------------- */
    #MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {{
        background-color: var(--bg-canvas) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1380px !important;
        margin: 0 auto !important;
    }}

    /* -------------------------------------------------------------------------
       3. Typography Rules
       ------------------------------------------------------------------------- */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-display) !important;
        font-weight: 700 !important;
        letter-spacing: -0.035em !important;
        line-height: 0.98 !important;
        color: var(--text-primary) !important;
    }}

    .display-title {{
        font-family: var(--font-display) !important;
        font-size: clamp(3.8rem, 8.5vw, 7.8rem) !important;
        font-weight: 700 !important;
        line-height: 0.92 !important;
        letter-spacing: -0.045em !important;
        color: var(--text-primary) !important;
        margin: 0 0 0.5rem 0 !important;
    }}

    .display-accent {{
        color: var(--accent) !important;
    }}

    .subtitle-label {{
        font-family: var(--font-mono) !important;
        font-size: 0.76rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.14em !important;
        color: var(--text-secondary) !important;
        margin-bottom: 1.25rem !important;
    }}

    .section-eyebrow {{
        font-family: var(--font-mono) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.16em !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.5rem !important;
    }}

    /* -------------------------------------------------------------------------
       4. Inputs (Borderless with Hairline Underline)
       ------------------------------------------------------------------------- */
    [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
    }}

    [data-baseweb="base-input"] {{
        background: transparent !important;
        border: none !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        border-radius: 0px !important;
        transition: border-color 0.15s ease !important;
    }}

    [data-baseweb="base-input"]:focus-within {{
        border-bottom: 1px solid var(--accent) !important;
    }}

    input[type="text"], input[type="password"], textarea {{
        background: transparent !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
        font-size: 0.95rem !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
    }}

    input::placeholder, textarea::placeholder {{
        color: var(--text-muted) !important;
        font-style: normal !important;
    }}

    /* Selectbox styling */
    div[data-testid="stSelectbox"] > div {{
        border: none !important;
    }}
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        border-radius: 0px !important;
        color: var(--text-primary) !important;
        padding-left: 0px !important;
    }}
    div[data-testid="stSelectbox"] [data-baseweb="select"]:hover > div {{
        border-bottom-color: var(--accent) !important;
    }}

    /* -------------------------------------------------------------------------
       5. Buttons (Flat, Sharp, Editorial)
       ------------------------------------------------------------------------- */
    .stButton > button {{
        background: transparent !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 0px !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }}

    .stButton > button:hover {{
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background: transparent !important;
        transform: none !important;
    }}

    .stButton > button[kind="primary"] {{
        background: var(--accent) !important;
        color: #0A0A0A !important;
        border: 1px solid var(--accent) !important;
        font-weight: 600 !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background: #00CBA7 !important;
        color: #0A0A0A !important;
        border-color: #00CBA7 !important;
    }}

    /* -------------------------------------------------------------------------
       6. Expanders (Hairline Borders Only, No Box Cards)
       ------------------------------------------------------------------------- */
    [data-testid="stExpander"] {{
        background: transparent !important;
        border: none !important;
        border-top: 1px solid var(--border-hairline) !important;
        border-bottom: 1px solid var(--border-hairline) !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        margin-top: 0.85rem !important;
    }}

    [data-testid="stExpander"] summary {{
        font-family: var(--font-mono) !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--text-secondary) !important;
        padding: 0.75rem 0 !important;
    }}

    [data-testid="stExpander"] summary:hover {{
        color: var(--text-primary) !important;
    }}

    /* -------------------------------------------------------------------------
       7. Hairlines & Dividers
       ------------------------------------------------------------------------- */
    .hairline {{
        border: none;
        border-top: 1px solid var(--border-hairline);
        margin: 1.5rem 0;
    }}

    .hairline-subtle {{
        border: none;
        border-top: 1px solid #1A1A1A;
        margin: 1rem 0;
    }}

    /* -------------------------------------------------------------------------
       8. Widget Labels & Scrollbars
       ------------------------------------------------------------------------- */
    [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p {{
        font-family: var(--font-mono) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.35rem !important;
    }}

    /* Icon button sizing */
    button:has([data-testid="stIconMaterial"]):not([kind="primary"]) {{
        border-color: var(--border-hairline) !important;
        padding: 0.45rem 0.65rem !important;
    }}

    /* Thin dark scrollbars */
    ::-webkit-scrollbar {{
        width: 4px;
        height: 4px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-canvas);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-subtle);
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--accent);
    }}

    /* -------------------------------------------------------------------------
       8. Minimal Tables / DataFrames
       ------------------------------------------------------------------------- */
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border-hairline) !important;
        border-radius: 0px !important;
    }}

    /* -------------------------------------------------------------------------
       9. Top Header Bar
       ------------------------------------------------------------------------- */
    .editorial-topbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0 1.2rem 0;
        border-bottom: 1px solid var(--border-hairline);
        margin-bottom: 2rem;
    }}

    .editorial-topbar-brand {{
        font-family: var(--font-display);
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: var(--text-primary);
    }}

    .editorial-topbar-user {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: var(--font-mono);
        font-size: 0.82rem;
        color: var(--text-secondary);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_header_html(user_name: str, designation: str = None) -> str:
    """Generates the clean, unboxed top bar header markup."""
    desig_snippet = f"<span style='color: var(--text-muted); font-size: 0.75rem;'>// {designation}</span>" if designation else ""
    return f"""
    <div class="editorial-topbar">
        <div class="editorial-topbar-brand">
            Util<span style="color: var(--accent);">{user_name.split()[0] if False else "Pulse"}</span>
        </div>
        <div class="editorial-topbar-user">
            <span style="color: var(--text-muted);">operator :</span>
            <span style="color: var(--text-primary); font-weight: 500;">{user_name}</span>
            {desig_snippet}
        </div>
    </div>
    """

"""
UtilPulse Command Centre — Minimal Editorial Components
=======================================================
Clean typographic elements: stats rows, capability rows, provenance lines,
and minimal KPIs without boxes, drop-shadows, or emojis.
"""

import streamlit as st


def render_stat_row(number_str: str, label_str: str):
    """Renders a minimal vertical statistic row with hairline separation."""
    html = f"""
    <div style="padding: 1.1rem 0; border-bottom: 1px solid #1F1F1F;">
        <div style="font-family: var(--font-display); font-size: clamp(2.2rem, 3.8vw, 3.2rem); font-weight: 700; color: #FFFFFF; line-height: 1; letter-spacing: -0.03em;">
            {number_str}
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.14em; color: #8A8A8A; margin-top: 0.35rem;">
            {label_str}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_capability_row(index_str: str, title_str: str, description_str: str):
    """Renders an editorial typographic capability row."""
    html = f"""
    <div style="padding: 1.6rem 0; border-bottom: 1px solid #1F1F1F;">
        <div style="display: flex; gap: 1.5rem; align-items: baseline;">
            <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent); letter-spacing: 0.1em;">
                {index_str}
            </span>
            <div style="flex: 1;">
                <div style="font-family: var(--font-display); font-size: 1.35rem; font-weight: 600; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 0.35rem;">
                    {title_str}
                </div>
                <div style="font-family: var(--font-body); font-size: 0.88rem; color: #8A8A8A; line-height: 1.55;">
                    {description_str}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_provenance_badge(provenance_text: str):
    """Renders clean, letter-spaced provenance information with a thin top divider."""
    html = f"""
    <div style="border-top: 1px solid #1F1F1F; padding-top: 0.85rem; margin-top: 1.75rem; margin-bottom: 0.75rem;">
        <div style="font-family: var(--font-mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.14em; color: #666666;">
            DATA PROVENANCE <span style="color: #444444; margin: 0 6px;">/</span> <span style="color: #999999;">{provenance_text}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_minimal_kpi(label: str, value_str: str, target_note: str, is_compliant: bool = True):
    """Renders a single unboxed KPI metric block."""
    val_color = "var(--accent)" if is_compliant else "#D9534F"
    html = f"""
    <div style="padding: 0.75rem 0; border-right: 1px solid #1F1F1F; padding-right: 1rem;">
        <div style="font-family: var(--font-mono); font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.12em; color: #8A8A8A; margin-bottom: 0.25rem;">
            {label}
        </div>
        <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 700; color: {val_color}; line-height: 1.1;">
            {value_str}
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.64rem; color: #555555; margin-top: 0.2rem;">
            {target_note}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_stat_box(val: str, label: str, icon: str = ""):
    """Compatibility wrapper for legacy stat calls."""
    render_stat_row(val, label)


def render_feature_card(icon: str, title: str, desc: str):
    """Compatibility wrapper for legacy feature calls."""
    render_capability_row("•", title, desc)

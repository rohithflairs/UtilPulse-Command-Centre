"""
UtilPulse Command Centre — Landing / Intro Page (Minimal Editorial Edition)
==========================================================================
Swiss-style, typography-first landing screen featuring two equal halves:
- Left: Massive title, editorial descriptor, and flat "Ask UtilPulse ->" trigger.
- Right: Minimal vertical stat list with hairlines, zero cards, zero emojis.
- Below Fold: Platform capabilities rendered as clean typographic index rows.
"""

import streamlit as st
from frontend.components import render_stat_row, render_capability_row


def render_home_page():
    """Renders the minimal editorial black & white intro screen."""

    # Top Hero Section: Two Equal Halves (50 / 50)
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown(
            """
            <div style="padding-top: clamp(2rem, 6vh, 5rem); padding-bottom: 2rem;">
                <h1 class="display-title">
                    Util<span class="display-accent">Pulse</span>
                </h1>
                <div class="subtitle-label">
                    Command Centre
                </div>
                <p style="font-family: var(--font-body); font-size: 1.05rem; color: var(--text-secondary); line-height: 1.65; max-width: 520px; margin-bottom: 2.25rem;">
                    Real-Time Conversational Intelligence Platform for Municipal Water Networks,
                    Asset Reliability, Hydro-Operations, and Water Quality Compliance.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Ask UtilPulse →", key="hero_access_btn", type="primary", icon=":material/arrow_forward:"):
            if st.session_state.get("authenticated", False):
                st.session_state.page = "chat"
            else:
                st.session_state.page = "login"
            st.rerun()

    with col_right:
        st.markdown(
            """
            <div style="padding-top: clamp(2rem, 6vh, 5rem); padding-bottom: 2rem;">
            """,
            unsafe_allow_html=True,
        )
        render_stat_row("163,904", "Telemetry Readings")
        render_stat_row("832", "Distribution Nodes")
        render_stat_row("10 Cities", "Metro Water Utilities")
        render_stat_row("51 Dimensions", "Sensors & Water Quality")
        st.markdown("</div>", unsafe_allow_html=True)

    # Hairline divider separating Hero from Capabilities
    st.markdown("<div style='height: clamp(3rem, 8vh, 6rem);'></div>", unsafe_allow_html=True)
    st.markdown("<hr class='hairline'>", unsafe_allow_html=True)

    # Below Fold Section: Platform Capabilities
    st.markdown(
        """
        <div style="margin-top: 2rem; margin-bottom: 2.5rem;">
            <div class="section-eyebrow">Platform Capabilities</div>
            <h2 style="font-family: var(--font-display); font-size: clamp(2rem, 4vw, 3rem); font-weight: 700; letter-spacing: -0.03em;">
                Engineering Architecture & Domain Intelligence
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cap_left, cap_right = st.columns([1, 1], gap="large")

    with cap_left:
        render_capability_row(
            "01",
            "Natural Language Queries",
            "Operators and reliability engineers ask questions in plain English. The platform interprets operational intent and queries complex sensor series without manual SQL.",
        )
        render_capability_row(
            "02",
            "Standards-Aware RAG",
            "Grounds responses in Indian Standard IS 10500:2012, CPHEEO guidelines, and WHO norms. Provides immediate potability, turbidity, and chlorine compliance analysis.",
        )
        render_capability_row(
            "03",
            "Loss & NRW Diagnostics",
            "Tracks Non-Revenue Water (NRW), pipe burst risk based on material and age, hydraulic head loss gradients, and service interruptions across municipal zones.",
        )

    with cap_right:
        render_capability_row(
            "04",
            "Dynamic Visual Analytics",
            "Generates real-time Plotly charts, correlation plots, comparative bar charts, and tabular diagnostics matching analytical intent.",
        )
        render_capability_row(
            "05",
            "Role-Based Security",
            "Enforces strict data access rules across Admin, Zone Operators, Quality Specialists, and Executive tiers with transparent data provenance.",
        )
        render_capability_row(
            "06",
            "Multi-City Coverage",
            "Full telemetry coverage across 10 metro water authorities including MCGM Mumbai, Delhi Jal Board, BWSSB Bangalore, HMWSSB Hyderabad, CMWSSB Chennai and 5 more.",
        )

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # Bottom minimal navigation link
    b_col1, b_col2 = st.columns([1, 1])
    with b_col1:
        if st.button("Ask UtilPulse →", key="sub_access_btn", icon=":material/arrow_forward:"):
            if st.session_state.get("authenticated", False):
                st.session_state.page = "chat"
            else:
                st.session_state.page = "login"
            st.rerun()

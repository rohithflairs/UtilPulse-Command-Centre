"""
UtilPulse Command Centre — Authorization / Login Page (Minimal Editorial Edition)
=================================================================================
Presents a pure, unboxed authorization interface:
- Top-left subtle back arrow.
- Display title "Authorize to use UtilPulse" + "Login" subheading.
- Borderless single-underline inputs for Operator ID / Username and Password.
- Flat "Continue ->" submission with full Enter-key support.
"""

import streamlit as st
from security.auth import Authenticator


def render_login_page():
    """Renders the minimal editorial authorization screen."""

    # Top-Left Subtle Navigation Back Arrow
    top_nav, _ = st.columns([1, 10])
    with top_nav:
        if st.button("Back", key="login_back_btn", icon=":material/arrow_back:"):
            st.session_state.page = "home"
            st.rerun()

    st.markdown("<div style='height: clamp(2rem, 5vh, 4rem);'></div>", unsafe_allow_html=True)

    # Centered narrow column layout with generous empty space
    _, col_center, _ = st.columns([1, 1.1, 1])

    with col_center:
        st.markdown(
            """
            <div style="margin-bottom: 2rem;">
                <h1 style="font-family: var(--font-display); font-size: clamp(2.2rem, 3.5vw, 3rem); font-weight: 700; letter-spacing: -0.035em; line-height: 1.05; margin-bottom: 0.4rem;">
                    Authorize to use UtilPulse
                </h1>
                <div style="font-family: var(--font-mono); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text-secondary);">
                    Login
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Operator ID / Username", key="login_username_input")
            password = st.text_input("Password", type="password", key="login_password_input")

            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

            submit_btn = st.form_submit_button(
                "Continue →",
                type="primary",
            )

            if submit_btn:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user_info = Authenticator.authenticate(username.strip(), password.strip())
                    if user_info:
                        st.session_state.authenticated = True
                        st.session_state.user = user_info
                        st.session_state.page = "chat"
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify your Operator ID and password.")

"""
UtilPulse Command Centre — Main Application Entry Point
=======================================================
Run this application via:
    streamlit run main.py
"""

import sys
import os

# Ensure the project root directory is in the Python system path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from frontend.styles import apply_custom_css
from frontend.home_page import render_home_page
from frontend.login_page import render_login_page
from frontend.chat_page import render_chat_page


def main():
    """Main routing and lifecycle controller for UtilPulse Command Centre."""

    # Streamlit page layout configuration
    st.set_page_config(
        page_title="UtilPulse Command Centre",
        page_icon=":material/water_drop:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Inject dark modern UI styling
    apply_custom_css()

    # Initialize navigation and session state variables
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None

    # Route based on active page state
    current_page = st.session_state.page

    if current_page == "home":
        render_home_page()
    elif current_page == "login":
        render_login_page()
    elif current_page == "chat":
        # Guard: if not authenticated, redirect to login
        if not st.session_state.authenticated:
            st.session_state.page = "login"
            st.rerun()
        else:
            render_chat_page()
    else:
        # Fallback to home
        st.session_state.page = "home"
        render_home_page()


if __name__ == "__main__":
    main()

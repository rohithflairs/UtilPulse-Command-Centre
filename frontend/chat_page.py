"""
UtilPulse Command Centre — Interactive Conversational Analytics Console
=======================================================================
Pure Minimal Edition with Domain Guardrails:
- Pure top bar: project name on left, user name + designation + logout icon on right.
- Left column (40%): "Ask UtilPulse", placeholder-free borderless input,
  Submit and Cancel text buttons (50/50 equal width below the input),
  collapsed "Suggested Inquiries" and "History" expanders with robust callbacks.
- Right column (60%): Pure Question and Answer response area (Query Response,
  Inquiry heading, LLM answer text, contextual charts, telemetry tables, and provenance).
  Strictly refuses to answer questions outside the water utility telemetry dataset.
"""

import streamlit as st
import pandas as pd
from security.security_gate import SecurityGate
from frontend.components import render_provenance_badge
from response.response_generator import OUT_OF_SCOPE_MESSAGE


def get_cached_modules():
    """Initializes and caches backend intelligence engines."""
    from database.data_loader import load_csv_to_sqlite
    from database.db_manager import run_query
    from llm.intent_parser import IntentParser
    from llm.query_engine import QueryEngine
    from rag.rag_engine import RAGEngine
    from response.response_generator import ResponseGenerator
    from response.chart_generator import ChartGenerator

    # Ensure SQLite database is primed
    load_csv_to_sqlite()

    return {
        "intent_parser": IntentParser(),
        "query_engine": QueryEngine(),
        "rag_engine": RAGEngine(),
        "response_gen": ResponseGenerator(),
        "chart_gen": ChartGenerator(),
    }


# -----------------------------------------------------------------------------
# Callback Handlers (Execute BEFORE widgets instantiate to avoid Streamlit errors)
# -----------------------------------------------------------------------------
def on_submit_query():
    """Callback triggered on 'Submit' button click."""
    raw_query = st.session_state.get("main_query_input_widget", "").strip()
    if raw_query:
        st.session_state["target_execution_query"] = raw_query
        st.session_state["main_query_input_widget"] = ""


def on_cancel_query():
    """Callback triggered on 'Cancel' button click."""
    st.session_state["main_query_input_widget"] = ""
    st.session_state["target_execution_query"] = None
    st.session_state["current_response"] = None


def on_preset_select(preset_text: str):
    """Callback triggered when selecting a suggested inquiry preset."""
    st.session_state["target_execution_query"] = preset_text
    st.session_state["main_query_input_widget"] = ""


def on_history_select(history_item: dict):
    """Callback triggered when selecting a query from session history."""
    st.session_state["current_response"] = history_item


def render_chat_page():
    """Renders the primary minimal editorial command centre interface."""
    user = st.session_state.get("user", {"name": "Operator", "designation": "Field Specialist", "role": "Admin"})
    user_name = user.get("name", "Operator")
    user_role = user.get("role", "")

    # Ensure session keys exist prior to widget render
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_response" not in st.session_state:
        st.session_state.current_response = None
    if "main_query_input_widget" not in st.session_state:
        st.session_state["main_query_input_widget"] = ""

    # -------------------------------------------------------------------------
    # 1. Top Bar (No Card, No Background, Pure Typography)
    # -------------------------------------------------------------------------
    col_brand, col_user, col_logout = st.columns([5, 2.2, 0.45], gap="small")

    with col_brand:
        st.markdown(
            """
            <div style="font-family: var(--font-display); font-size: 1.6rem; font-weight: 700; letter-spacing: -0.04em;">
                Util<span style="color: var(--accent);">Pulse</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_user:
        role_label = f"// {user_role}" if user_role else ""
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 6px; font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-secondary);">
                <svg style="vertical-align: -2px; width: 14px; height: 14px; fill: none; stroke: currentColor; stroke-width: 1.5; margin-right: 4px;" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                <span style="color: var(--text-primary); font-weight: 500;">{user_name}</span>
                <span style="color: #555555; margin-left: 4px;">{role_label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_logout:
        if st.button("", key="logout_btn", icon=":material/logout:", help="End Session & Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.session_state.current_response = None
            st.session_state.page = "home"
            st.rerun()

    st.markdown("<hr class='hairline' style='margin-top: 0.5rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    # Instantiate security gate for active user role
    security_gate = SecurityGate(user.get("role", "Admin"))

    # Load Backend Engines
    try:
        if "backend_engines" not in st.session_state:
            with st.spinner("Initializing telemetry indices and analytical models..."):
                st.session_state.backend_engines = get_cached_modules()
        engines = st.session_state.backend_engines
    except Exception as e:
        st.error(f"Engine initialization error: {str(e)}")
        return

    # Two-Column Body: 40% Left / 60% Right
    left_col, right_col = st.columns([40, 60], gap="large")

    # =========================================================================
    # LEFT COLUMN: ASK UTILPULSE, INPUT, ACTIONS, EXPANDERS
    # =========================================================================
    with left_col:
        st.markdown(
            """
            <h2 style="font-family: var(--font-display); font-size: 1.8rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 1.2rem;">
                Ask UtilPulse
            </h2>
            """,
            unsafe_allow_html=True,
        )

        # Single borderless input with NO placeholder text
        query_input = st.text_area(
            label="Ask UtilPulse query",
            height=95,
            placeholder="",
            key="main_query_input_widget",
            label_visibility="collapsed",
        )

        # Normal text buttons (Submit and Cancel) equal sizes half-and-half spanning below the input
        col_submit, col_cancel = st.columns([1, 1], gap="small")
        with col_submit:
            st.button(
                "Submit",
                key="btn_query_submit",
                type="primary",
                use_container_width=True,
                on_click=on_submit_query,
            )
        with col_cancel:
            st.button(
                "Cancel",
                key="btn_query_cancel",
                use_container_width=True,
                on_click=on_cancel_query,
            )

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Collapsed Suggested Inquiries Expander
        with st.expander("Suggested Inquiries", expanded=False):
            preset_questions = [
                "Is the water in Mumbai safe to drink?",
                "What is the overall pressure compliance rate across all cities?",
                "Which city has the highest non-revenue water percentage?",
                "Compare chlorine compliance rates across all 10 cities",
                "Show monthly supply hours trend for Delhi Jal Board",
                "Does Zone A in Delhi have cast iron pipes?",
                "What are the IS 10500 standards for residual chlorine and turbidity?",
            ]
            for idx, preset in enumerate(preset_questions):
                st.button(
                    preset,
                    key=f"preset_btn_{idx}",
                    use_container_width=True,
                    on_click=on_preset_select,
                    args=(preset,),
                )

        # Collapsed History Expander (preserves history feature)
        with st.expander("History", expanded=False):
            if st.session_state.chat_history:
                for h_idx, item in enumerate(reversed(st.session_state.chat_history)):
                    q_text = item["question"]
                    display_q = q_text if len(q_text) <= 50 else q_text[:48] + "..."
                    st.button(
                        display_q,
                        key=f"hist_btn_{h_idx}",
                        use_container_width=True,
                        on_click=on_history_select,
                        args=(item,),
                    )
            else:
                st.caption("No queries executed yet.")

    # =========================================================================
    # RIGHT COLUMN: QUERY RESPONSE (QUESTION & ANSWER ONLY)
    # =========================================================================
    with right_col:
        # Trigger Execution Logic
        target_question = st.session_state.pop("target_execution_query", None)

        if target_question:
            with st.spinner("Analyzing operational telemetry and generating response..."):
                try:
                    # 1. Intent Parsing with Domain Scope Check
                    intent = engines["intent_parser"].parse(target_question)

                    # Strict Domain Boundary Enforcement
                    if not intent.get("is_domain_relevant", True) or intent.get("intent_type") == "out_of_scope":
                        response_payload = {
                            "question": target_question,
                            "answer": OUT_OF_SCOPE_MESSAGE,
                            "dataframe": None,
                            "sql": None,
                            "provenance": None,
                            "chart": None,
                            "intent": intent,
                        }
                        st.session_state.current_response = response_payload
                        st.session_state.chat_history.append(response_payload)
                    else:
                        # 2. Security Permission Check
                        allowed, sec_err = security_gate.check_query_allowed(intent)
                        if not allowed:
                            st.error(f"Access Restriction: {sec_err}")
                            return

                        # 3. Standards Retrieval (RAG)
                        rag_context = engines["rag_engine"].retrieve_context(target_question, top_k=3)

                        # 4. SQL Telemetry Execution
                        df_results, sql_executed, query_err = engines["query_engine"].generate_and_execute(intent, target_question)

                        # 5. Security Column/Row Filtering
                        df_filtered = security_gate.filter_results(df_results, intent)

                        # 6. Provenance Generation
                        provenance_str = engines["query_engine"].get_data_provenance(intent, df_filtered)

                        # 7. LLM Natural Language Response Generation
                        answer_text = engines["response_gen"].generate(
                            user_question=target_question,
                            intent=intent,
                            query_results_df=df_filtered,
                            sql_query=sql_executed,
                            rag_context=rag_context,
                            provenance=provenance_str,
                        )

                        # 8. Chart Generation (ONLY when expected and meaningful)
                        fig = engines["chart_gen"].create_chart(df_filtered, intent)

                        # Save Result to State and History
                        response_payload = {
                            "question": target_question,
                            "answer": answer_text,
                            "dataframe": df_filtered,
                            "sql": sql_executed,
                            "provenance": provenance_str,
                            "chart": fig,
                            "intent": intent,
                        }
                        st.session_state.current_response = response_payload
                        st.session_state.chat_history.append(response_payload)

                except Exception as e:
                    st.error(f"Analytical pipeline execution error: {str(e)}")

        # Heading: Query Response
        st.markdown(
            """
            <h2 style="font-family: var(--font-display); font-size: 1.8rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 1.2rem;">
                Query Response
            </h2>
            """,
            unsafe_allow_html=True,
        )

        # DISPLAY ACTIVE RESPONSE (Or empty space if no query run yet)
        resp = st.session_state.current_response
        if resp:
            st.markdown(
                f"""
                <div style="font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text-secondary); margin-bottom: 0.75rem;">
                    INQUIRY <span style="color: #444444; margin: 0 4px;">//</span> <span style="color: var(--text-primary);">{resp['question']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Main LLM Text Answer in readable body font
            st.markdown(
                f"""
                <div style="font-family: var(--font-body); font-size: 0.96rem; line-height: 1.7; color: var(--text-primary); max-width: 820px; margin-bottom: 1.5rem;">
                {resp["answer"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ONLY Render Chart if a chart was generated and expected
            if resp.get("chart") is not None:
                st.plotly_chart(resp["chart"], use_container_width=True)

            # Data Table Drilldown (Only when multiple rows are returned and chart was expected or comparison done)
            df_table = resp.get("dataframe")
            chart_type_val = resp.get("intent", {}).get("chart_type", "none")
            if df_table is not None and not df_table.empty and len(df_table) > 1 and chart_type_val != "none":
                with st.expander(f"Telemetry Data ({len(df_table)} rows)", expanded=False):
                    st.dataframe(df_table, use_container_width=True)

            # Data Provenance Badge
            if resp.get("provenance") and resp.get("sql"):
                render_provenance_badge(resp["provenance"])

            # SQL Audit Inspector (only if SQL was actually executed)
            if resp.get("sql"):
                with st.expander("SQL Audit Inspector", expanded=False):
                    st.code(resp["sql"], language="sql")
        else:
            # Clean empty space when no query has been run yet (pure whitespace)
            st.markdown("<div style='height: 160px;'></div>", unsafe_allow_html=True)

"""
UtilPulse Command Centre — Query Engine (Groq Powered)
=======================================================
Generates SQL from parsed intent via Groq API, validates it for
strict read-only safety, and executes it against the SQLite database.
"""

import json
import os
import re
import pandas as pd
from config import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_BACKUP_MODEL,
    VALID_COLUMNS,
    TABLE_NAME,
    MAX_QUERY_RESULTS,
    PROMPTS_DIR,
)
from database.db_manager import run_query


class QueryEngine:
    """Translates user intent into safe SQL via Groq, executes it, and returns results."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = None
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception:
                self.client = None

        prompt_path = os.path.join(PROMPTS_DIR, "sql_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as fh:
                self.sql_template = fh.read()
        else:
            self.sql_template = ""

    def generate_and_execute(self, intent: dict, user_question: str):
        """Generates SQL from intent, validates safety, executes against SQLite,
        and returns (DataFrame, sql_string, error_or_None)."""
        if intent.get("intent_type") == "general_knowledge" and not intent.get("metrics"):
            return pd.DataFrame(), "", None

        sql = ""
        # 1. Attempt Groq SQL generation
        if self.client:
            prompt = (
                self.sql_template
                .replace("{valid_columns}", ", ".join(VALID_COLUMNS))
                .replace("{max_rows}", str(MAX_QUERY_RESULTS))
                .replace("{intent_json}", json.dumps(intent, indent=2, default=str))
                .replace("{user_question}", user_question)
            )

            for model_candidate in [LLM_MODEL, LLM_BACKUP_MODEL]:
                try:
                    chat_resp = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a professional SQLite database specialist. Output ONLY valid SQL with no explanations."},
                            {"role": "user", "content": prompt}
                        ],
                        model=model_candidate,
                        temperature=0.0,
                    )
                    raw_sql = chat_resp.choices[0].message.content.strip()
                    raw_sql = re.sub(r"^```sql\s*", "", raw_sql, flags=re.IGNORECASE)
                    raw_sql = re.sub(r"^```\s*", "", raw_sql, flags=re.IGNORECASE)
                    raw_sql = re.sub(r"\s*```$", "", raw_sql, flags=re.IGNORECASE).strip()

                    val_err = self._validate_sql(raw_sql)
                    if not val_err:
                        sql = raw_sql
                        break
                except Exception:
                    continue

        # 2. Rule-based SQL generation fallback if Groq failed or was offline
        if not sql:
            sql = self._build_deterministic_sql(intent, user_question)

        # 3. Final validation and execution
        val_err = self._validate_sql(sql)
        if val_err:
            return pd.DataFrame(), sql, val_err

        try:
            df = run_query(sql)
            return df, sql, None
        except Exception as exc:
            return pd.DataFrame(), sql, f"Query execution error: {exc}"

    def _build_deterministic_sql(self, intent: dict, q: str) -> str:
        """Deterministic query constructor for water utility inquiries."""
        metrics = intent.get("metrics", [])
        group_by = intent.get("group_by", [])
        filters = intent.get("filters", {})
        limit = intent.get("limit") or 20

        select_items = []
        for g in group_by:
            if g in VALID_COLUMNS:
                select_items.append(g)

        if not metrics:
            metrics = ["inlet_pressure_bar", "non_revenue_water_pct"]

        for m in metrics:
            if m not in VALID_COLUMNS:
                continue
            if "flag" in m:
                select_items.append(f"ROUND(AVG({m}) * 100, 2) AS {m.replace('_flag', '_compliance_pct')}")
            elif "events" in m or "interruptions" in m:
                select_items.append(f"SUM({m}) AS total_{m}")
            else:
                select_items.append(f"ROUND(AVG({m}), 2) AS avg_{m}")

        if not select_items:
            select_items = ["ROUND(AVG(non_revenue_water_pct), 2) AS avg_nrw_pct"]

        where_clauses = []
        for k, v in filters.items():
            if v and k in VALID_COLUMNS:
                where_clauses.append(f"{k} = '{v}'")

        select_str = ", ".join(select_items)
        where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        group_str = f"GROUP BY {', '.join(group_by)}" if group_by else ""

        order_col = select_items[-1].split(" AS ")[-1] if select_items else "1"
        order_str = f"ORDER BY {order_col} DESC" if group_by else ""
        limit_str = f"LIMIT {limit}" if group_by else ""

        sql = f"SELECT {select_str} FROM {TABLE_NAME} {where_str} {group_str} {order_str} {limit_str}".strip()
        sql = re.sub(r"\s+", " ", sql)
        return sql

    def _validate_sql(self, sql: str):
        """Validates SQL query against security boundaries."""
        if not sql or not sql.strip():
            return "Empty SQL statement."

        sql_upper = sql.upper().strip()
        if not sql_upper.startswith("SELECT"):
            return "Security violation: Only SELECT queries are permitted."

        blocked = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "EXEC", "--"]
        clean_check = sql_upper.rstrip(";")

        for token in blocked:
            if token == "--" and token in clean_check:
                return "Comments (--) are forbidden in operational queries."
            pattern = rf"\b{token}\b"
            if re.search(pattern, clean_check):
                return f"Security violation: Forbidden keyword '{token}' detected."

        if TABLE_NAME.upper() not in sql_upper:
            return f"Query must target the '{TABLE_NAME}' telemetry repository."

        return None

    def get_data_provenance(self, intent: dict, df: pd.DataFrame) -> str:
        """Constructs audit trail string indicating sources and telemetry scope."""
        parts = []
        if df is not None and not df.empty:
            parts.append(f"{len(df)} analytical records")

        filters = intent.get("filters", {})
        filter_snippets = [f"{k}: {v}" for k, v in filters.items() if v]
        if filter_snippets:
            parts.append(f"Scope: {', '.join(filter_snippets)}")
        else:
            parts.append("Scope: Municipal Network-wide (10 Utilities, 832 Nodes)")

        parts.append("Telemetry Period: Jan 1 – Jul 15, 2024 (197 Daily Cycles)")
        return " | ".join(parts)

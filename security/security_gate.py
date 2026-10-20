"""
UtilPulse Command Centre — Security Gate
==========================================
Role-based access control layer that filters query results and restricts
operations according to the user's assigned role.
"""

import pandas as pd
from config import ROLES


class SecurityGate:
    """Enforces role-based data filtering and query restrictions."""

    def __init__(self, role: str = "Admin"):
        self.role = role
        self.role_config = ROLES.get(role, ROLES["Admin"])

    def filter_results(self, df: pd.DataFrame, intent: dict | None = None) -> pd.DataFrame:
        """Filter DataFrame columns based on role permissions.

        Parameters
        ----------
        df : pd.DataFrame
            Raw query results.
        intent : dict | None
            Parsed intent (reserved for future per-intent filtering).

        Returns
        -------
        pd.DataFrame
            Filtered DataFrame with only the columns the role may see.
        """
        if df.empty or self.role == "Admin":
            return df

        filtered = df.copy()

        # Column-level filtering
        allowed_cols = self.role_config.get("allowed_columns")
        if allowed_cols != "all":
            valid_cols = [c for c in filtered.columns if c in allowed_cols]
            if valid_cols:
                filtered = filtered[valid_cols]

        # Node-level visibility restriction
        if not self.role_config.get("can_see_node_level", True):
            if "node_id" in filtered.columns:
                filtered = filtered.drop(columns=["node_id"], errors="ignore")

        return filtered

    def check_query_allowed(self, intent: dict) -> tuple[bool, str]:
        """Check whether the current role is permitted to execute the query.

        Parameters
        ----------
        intent : dict
            Parsed intent containing ``group_by`` and other fields.

        Returns
        -------
        tuple[bool, str]
            ``(allowed, message)`` — *message* explains the restriction when
            *allowed* is ``False``.
        """
        if self.role == "Admin":
            return True, ""

        if self.role == "Executive":
            group_by = intent.get("group_by", [])
            if "node_id" in group_by:
                return False, (
                    "Executive role can only access city-level aggregated data. "
                    "Node-level details are restricted."
                )

        return True, ""

    def get_access_notice(self) -> str:
        """Return a short markdown badge describing the active role."""
        return f"🔒 **{self.role}** — {self.role_config['description']}"

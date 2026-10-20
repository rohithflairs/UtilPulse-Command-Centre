"""
UtilPulse Command Centre — Chart Generator (Minimal Editorial Theme)
=====================================================================
Builds Plotly charts from query-result DataFrames, auto-selecting the best
visualisation type based on the parsed intent. Applies transparent canvas,
hairline gridlines (#1F1F1F), and the primary accent color (#00E0B8).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Colour palette (Primary accent #00E0B8 + editorial grays/white) ──────────
ACCENT = "#00E0B8"
COLORS = ["#00E0B8", "#FFFFFF", "#8A8A8A", "#CCCCCC", "#555555"]

CHART_HEIGHT = 400
CHART_TEMPLATE = "plotly_dark"


class ChartGenerator:
    """Creates Plotly figures tailored to UtilPulse data and intents."""

    # ── public entry point ──────────────────────────────────────────────────
    def create_chart(self, df: pd.DataFrame, intent: dict):
        """Dispatch to the right chart type based on the intent.

        Parameters
        ----------
        df : pd.DataFrame
            Query-result data.
        intent : dict
            Parsed intent containing ``chart_type``, ``group_by``, ``metrics``,
            etc.

        Returns
        -------
        plotly.graph_objects.Figure | None
            A ready-to-render Plotly figure, or *None* when no chart can be
            produced.
        """
        if df is None or df.empty:
            return None

        # 1. Strictly check if intent opted out of charts
        chart_type = str(intent.get("chart_type") or "none").lower().strip()
        if chart_type in ["none", "no", "null", "false", ""]:
            return None

        # 2. Never show charts for single-row results (scalars, single stats, or single lookups)
        # Visual charts are only meaningful when comparing 2 or more entities/points
        if len(df) <= 1:
            return None

        # 3. Suppress charts for Yes/No questions unless explicitly requested
        orig_q = str(intent.get("_original_question", "")).strip().lower()
        yes_no_starters = ("is ", "are ", "does ", "do ", "can ", "has ", "have ", "was ", "were ", "will ", "would ")
        chart_keywords = ("chart", "plot", "graph", "trend", "visual", "visualize", "diagram")
        if orig_q.startswith(yes_no_starters) and not any(k in orig_q for k in chart_keywords):
            return None

        group_by = intent.get("group_by", [])
        metrics = intent.get("metrics", [])

        # Check existing columns
        valid_group = [c for c in group_by if c in df.columns]
        if not valid_group:
            valid_group = self._detect_group_columns(df)
        group_by = valid_group

        # Check metric columns in df or match by substring
        valid_metrics = []
        for m in metrics:
            for col in df.columns:
                if m == col or m.lower() in col.lower() or col.lower() in m.lower():
                    if col not in valid_metrics and col not in group_by:
                        valid_metrics.append(col)

        # Fallback to all numeric non-grouping columns in df
        if not valid_metrics:
            valid_metrics = [c for c in self._detect_metric_columns(df) if c not in group_by]
            if not valid_metrics:
                # Any numeric column at all
                valid_metrics = [c for c in df.select_dtypes(include="number").columns if c not in group_by]

        metrics = valid_metrics

        if not metrics:
            return None

        # ── Dispatch ────────────────────────────────────────────────────
        try:
            if chart_type == "line":
                fig = self._line_chart(df, group_by, metrics)
            elif chart_type == "scatter":
                fig = self._scatter_chart(df, metrics)
            elif chart_type == "heatmap":
                fig = self._heatmap(df, group_by, metrics)
            else:
                # Default: bar
                fig = self._bar_chart(df, group_by, metrics)

            if fig:
                self._apply_editorial_theme(fig)
            return fig
        except Exception:
            # Graceful degradation — never crash the app over a chart
            return None

    def _apply_editorial_theme(self, fig):
        """Applies transparent background, hairline gridlines, and clean typography."""
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#8A8A8A", size=11),
            margin=dict(l=40, r=20, t=30, b=40),
            xaxis=dict(
                gridcolor="#1F1F1F",
                zerolinecolor="#1F1F1F",
                linecolor="#1F1F1F",
                tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#8A8A8A"),
                title_font=dict(family="Inter, sans-serif", size=11, color="#8A8A8A"),
            ),
            yaxis=dict(
                gridcolor="#1F1F1F",
                zerolinecolor="#1F1F1F",
                linecolor="#1F1F1F",
                tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#8A8A8A"),
                title_font=dict(family="Inter, sans-serif", size=11, color="#8A8A8A"),
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(family="Inter, sans-serif", size=10, color="#CCCCCC"),
            ),
        )

    # ── bar chart ───────────────────────────────────────────────────────────
    def _bar_chart(self, df: pd.DataFrame, group_by: list, metrics: list):
        """Grouped / simple bar chart."""
        x_col = group_by[0] if group_by else df.columns[0]
        y_col = metrics[0]

        # If more than one metric, use a grouped bar
        if len(metrics) > 1:
            melted = df.melt(
                id_vars=[x_col],
                value_vars=metrics,
                var_name="Metric",
                value_name="Value",
            )
            fig = px.bar(
                melted,
                x=x_col,
                y="Value",
                color="Metric",
                barmode="group",
                template=CHART_TEMPLATE,
                height=CHART_HEIGHT,
                color_discrete_sequence=COLORS,
            )
        else:
            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                template=CHART_TEMPLATE,
                height=CHART_HEIGHT,
                color_discrete_sequence=COLORS,
            )

        fig.update_layout(
            xaxis_title=self._pretty(x_col),
            yaxis_title=self._pretty(y_col) if len(metrics) == 1 else "Value",
        )
        return fig

    # ── line chart ──────────────────────────────────────────────────────────
    def _line_chart(self, df: pd.DataFrame, group_by: list, metrics: list):
        """Multi-line chart with markers."""
        x_col = group_by[0] if group_by else df.columns[0]

        fig = go.Figure()
        for idx, metric in enumerate(metrics):
            if metric not in df.columns:
                continue
            color = COLORS[idx % len(COLORS)]
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=df[metric],
                    mode="lines+markers",
                    name=self._pretty(metric),
                    line=dict(color=color, width=1.5),
                    marker=dict(size=5),
                )
            )

        fig.update_layout(
            template=CHART_TEMPLATE,
            height=CHART_HEIGHT,
            xaxis_title=self._pretty(x_col),
            yaxis_title="Value",
        )
        return fig

    # ── scatter chart ───────────────────────────────────────────────────────
    def _scatter_chart(self, df: pd.DataFrame, metrics: list):
        """Scatter with OLS trendline (needs ≥ 2 numeric columns)."""
        if len(metrics) < 2:
            return None

        x_col, y_col = metrics[0], metrics[1]

        # Ensure numeric
        plot_df = df[[x_col, y_col]].dropna()
        try:
            plot_df[x_col] = pd.to_numeric(plot_df[x_col])
            plot_df[y_col] = pd.to_numeric(plot_df[y_col])
        except (ValueError, TypeError):
            return None

        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            template=CHART_TEMPLATE,
            height=CHART_HEIGHT,
            color_discrete_sequence=COLORS,
        )
        fig.update_layout(
            xaxis_title=self._pretty(x_col),
            yaxis_title=self._pretty(y_col),
        )
        return fig

    # ── heatmap ─────────────────────────────────────────────────────────────
    def _heatmap(self, df: pd.DataFrame, group_by: list, metrics: list):
        """Heatmap — needs at least two grouping dimensions + one metric."""
        if len(group_by) < 2 or not metrics:
            return self._bar_chart(df, group_by, metrics)

        x_col, y_col = group_by[0], group_by[1]
        z_col = metrics[0]

        try:
            pivot = df.pivot_table(index=y_col, columns=x_col, values=z_col, aggfunc="mean")
        except Exception:
            return self._bar_chart(df, group_by, metrics)

        fig = px.imshow(
            pivot,
            template=CHART_TEMPLATE,
            height=CHART_HEIGHT,
            color_continuous_scale=["#111111", "#00E0B8", "#FFFFFF"],
            aspect="auto",
        )
        fig.update_layout(
            xaxis_title=self._pretty(x_col),
            yaxis_title=self._pretty(y_col),
        )
        return fig

    # ── helpers ─────────────────────────────────────────────────────────────
    @staticmethod
    def _detect_group_columns(df: pd.DataFrame) -> list:
        """Pick likely categorical / grouping columns from the DataFrame."""
        candidates = [
            "city", "zone_id", "utility_name", "state", "node_type",
            "pipe_material", "demand_category", "season", "month_name",
            "day_of_week", "observation_date", "node_id",
        ]
        found = [c for c in candidates if c in df.columns]
        for c in df.select_dtypes(include=["object", "category"]).columns:
            if c not in found:
                found.append(c)
        return found[:2]

    @staticmethod
    def _detect_metric_columns(df: pd.DataFrame) -> list:
        """Pick likely numeric / metric columns from the DataFrame."""
        skip = {
            "record_id", "node_id", "month_num", "is_weekend",
            "pressure_compliance_flag", "chlorine_compliance_flag",
        }
        return [
            c
            for c in df.select_dtypes(include="number").columns
            if c not in skip
        ][:5]

    @staticmethod
    def _pretty(col_name: str) -> str:
        """Turn a snake_case column name into a human-friendly title."""
        return col_name.replace("_", " ").title()

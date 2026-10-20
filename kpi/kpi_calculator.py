"""
UtilPulse Command Centre — KPI Calculator
==========================================
Computes high-level Key Performance Indicators from the ``water_nodes``
table, with optional city / zone filtering.
"""

from database.db_manager import run_query


class KPICalculator:
    """Calculates operational KPIs for the UtilPulse dashboard."""

    def get_overview_kpis(self, city=None, zone=None) -> dict:
        """Return a dict of headline KPIs, optionally filtered by city/zone.

        KPIs returned
        -------------
        total_nodes, total_observations, pressure_compliance_pct,
        chlorine_compliance_pct, avg_nrw_pct, avg_supply_hours,
        leaks_per_node, avg_ph, avg_turbidity, avg_chlorine, avg_daily_volume

        Parameters
        ----------
        city : str | None
            Filter by city name (e.g. ``"Mumbai"``).
        zone : str | None
            Filter by zone_id (e.g. ``"Zone_A"``).

        Returns
        -------
        dict
            Column-name → value mapping.  Empty dict on failure.
        """
        conditions = []
        params: list = []

        if city:
            conditions.append("city = ?")
            params.append(city)
        if zone:
            conditions.append("zone_id = ?")
            params.append(zone)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = f"""
        SELECT
            COUNT(DISTINCT node_id)                              AS total_nodes,
            COUNT(*)                                             AS total_observations,
            ROUND(AVG(pressure_compliance_flag) * 100, 1)        AS pressure_compliance_pct,
            ROUND(AVG(chlorine_compliance_flag) * 100, 1)        AS chlorine_compliance_pct,
            ROUND(AVG(non_revenue_water_pct), 1)                 AS avg_nrw_pct,
            ROUND(AVG(supply_hours_per_day), 1)                  AS avg_supply_hours,
            ROUND(
                CAST(SUM(leak_detection_events) AS REAL)
                / NULLIF(COUNT(DISTINCT node_id), 0), 2)         AS leaks_per_node,
            ROUND(AVG(ph_value), 2)                              AS avg_ph,
            ROUND(AVG(turbidity_ntu), 2)                         AS avg_turbidity,
            ROUND(AVG(residual_chlorine_mg_l), 2)                AS avg_chlorine,
            ROUND(AVG(daily_volume_m3), 2)                       AS avg_daily_volume
        FROM water_nodes
        {where_clause}
        """

        df = run_query(sql, params if params else None)

        if df.empty:
            return {}

        return df.iloc[0].to_dict()

    def get_city_comparison(self):
        """Return a DataFrame comparing all 10 cities on key metrics.

        Returns
        -------
        pd.DataFrame
            One row per city with aggregated KPIs.
        """
        sql = """
        SELECT city,
            ROUND(AVG(pressure_compliance_flag)*100,1) as pressure_compliance,
            ROUND(AVG(chlorine_compliance_flag)*100,1) as chlorine_compliance,
            ROUND(AVG(non_revenue_water_pct),1)        as avg_nrw,
            ROUND(AVG(supply_hours_per_day),1)         as avg_supply_hours,
            ROUND(AVG(inlet_pressure_bar),2)           as avg_pressure,
            COUNT(DISTINCT node_id)                    as nodes
        FROM water_nodes
        GROUP BY city
        ORDER BY city
        """
        return run_query(sql)

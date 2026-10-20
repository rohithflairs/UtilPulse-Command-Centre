"""
UtilPulse Command Centre — CSV-to-SQLite Data Loader
=====================================================
Reads the master CSV dataset and loads it into a local SQLite database,
creating performance indexes on commonly filtered / joined columns.
"""

import os
import sqlite3
import pandas as pd

try:
    from config import CSV_PATH, DB_PATH, TABLE_NAME
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import CSV_PATH, DB_PATH, TABLE_NAME


def load_csv_to_sqlite(force_reload: bool = False) -> bool:
    """Load *Datasets/util_12.csv* into SQLite at ``config.DB_PATH``.

    Parameters
    ----------
    force_reload : bool, optional
        When *True* the existing database file is deleted and recreated
        from the CSV.  When *False* (default) the function is a no-op if
        the database already exists.

    Returns
    -------
    bool
        *True* if the data was (re-)loaded, *False* if loading was skipped
        because the database already existed.
    """
    # Skip if DB exists and no forced reload requested
    if os.path.exists(DB_PATH) and not force_reload:
        print(f"[data_loader] Database already exists at {DB_PATH} - skipping load.")
        return False

    # Remove stale DB when force-reloading
    if os.path.exists(DB_PATH) and force_reload:
        os.remove(DB_PATH)
        print(f"[data_loader] Removed existing database for force reload.")

    # Ensure the target directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # ------------------------------------------------------------------
    # Read CSV
    # ------------------------------------------------------------------
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")

    print(f"[data_loader] Reading CSV from {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH)
    print(f"[data_loader] Loaded {len(df):,} rows x {len(df.columns)} columns.")

    # ------------------------------------------------------------------
    # Write to SQLite
    # ------------------------------------------------------------------
    conn = sqlite3.connect(DB_PATH)
    try:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        print(f"[data_loader] Wrote table '{TABLE_NAME}' to {DB_PATH}.")

        # --------------------------------------------------------------
        # Create single-column indexes
        # --------------------------------------------------------------
        single_index_cols = [
            "node_id",
            "city",
            "zone_id",
            "utility_name",
            "observation_date",
            "pipe_material",
            "demand_category",
            "season",
            "node_type",
            "state",
        ]
        cursor = conn.cursor()
        for col in single_index_cols:
            idx_name = f"idx_{TABLE_NAME}_{col}"
            cursor.execute(
                f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{TABLE_NAME}" ("{col}")'
            )
            print(f"[data_loader] Created index {idx_name}.")

        # --------------------------------------------------------------
        # Composite index on (city, zone_id, observation_date)
        # --------------------------------------------------------------
        composite_idx = f"idx_{TABLE_NAME}_city_zone_date"
        cursor.execute(
            f'CREATE INDEX IF NOT EXISTS "{composite_idx}" '
            f'ON "{TABLE_NAME}" ("city", "zone_id", "observation_date")'
        )
        print(f"[data_loader] Created composite index {composite_idx}.")

        conn.commit()
    finally:
        conn.close()

    print("[data_loader] Database initialisation complete [OK]")
    return True


# Allow direct invocation: python -m database.data_loader
if __name__ == "__main__":
    load_csv_to_sqlite(force_reload=True)

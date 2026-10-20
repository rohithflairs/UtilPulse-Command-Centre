"""
UtilPulse Command Centre — Database Manager
=============================================
Lightweight helper layer around SQLite: connection factory, safe query
execution, and schema introspection.
"""

import os
import sqlite3
import pandas as pd

try:
    from config import DB_PATH, TABLE_NAME
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import DB_PATH, TABLE_NAME


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection to the project database.

    Raises
    ------
    FileNotFoundError
        If the database file does not exist yet (run ``data_loader`` first).
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. "
            "Run data_loader.load_csv_to_sqlite() first."
        )
    conn = sqlite3.connect(DB_PATH)
    return conn


def run_query(sql: str, params: tuple | list | None = None) -> pd.DataFrame:
    """Execute *sql* against the project database and return a DataFrame.

    Parameters
    ----------
    sql : str
        A valid SQLite SELECT statement.
    params : tuple | list | None, optional
        Bind parameters for the query.

    Returns
    -------
    pd.DataFrame
        Query results.  An **empty** DataFrame is returned when the query
        fails (the error is printed to stdout for debugging).
    """
    conn = None
    try:
        conn = get_connection()
        if params:
            df = pd.read_sql_query(sql, conn, params=params)
        else:
            df = pd.read_sql_query(sql, conn)
        return df
    except Exception as exc:
        print(f"[db_manager] Query error: {exc}")
        print(f"[db_manager] SQL was: {sql}")
        return pd.DataFrame()
    finally:
        if conn is not None:
            conn.close()


def get_table_info() -> pd.DataFrame:
    """Return column metadata via ``PRAGMA table_info`` for the main table.

    Returns
    -------
    pd.DataFrame
        Columns: cid, name, type, notnull, dflt_value, pk
    """
    return run_query(f'PRAGMA table_info("{TABLE_NAME}")')


# Quick smoke-test when run directly
if __name__ == "__main__":
    info = get_table_info()
    if info.empty:
        print("[db_manager] No table info — is the database loaded?")
    else:
        print(f"[db_manager] Table '{TABLE_NAME}' has {len(info)} columns:")
        for _, row in info.iterrows():
            print(f"  {row['name']:40s}  {row['type']}")

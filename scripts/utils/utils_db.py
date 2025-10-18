# utils_db.py

import logging
import sqlite3

def connect_to_db(db_path: str) -> sqlite3.Connection:
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        logging.error(f"Failed to connect to database at {db_path}: {e}")
        raise

def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if a table exists in the SQLite database."""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?;
        """, (table_name,))
    except Exception as e:
        logging.error(f"Failed to run check on existence of {table_name} in database: {e}")
        return False
    return cursor.fetchone() is not None

def get_table_schema(conn: sqlite3.Connection, table_name: str) -> list[dict]:
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
    except Exception as e:
        logging.error(f"Failed to run PRAGMA table_info({table_name}): {e}")
        return []
    rows = cursor.fetchall()
    return [
        {
            "cid": row[0],
            "name": row[1],
            "type": row[2],
            "notnull": bool(row[3]),
            "dflt_value": row[4],
            "pk": bool(row[5])
        }
        for row in rows
    ]

def get_tables_from_db(conn, layer: str = "") -> set[str]:
    like_clause = f"{layer}_%" if layer else "%"
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", (like_clause,)
        )
    except Exception as e:
        logging.error(f"Failed to select tables from database: {e}")
        raise
    return set(row[0] for row in cursor.fetchall())

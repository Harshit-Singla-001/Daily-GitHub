import sqlite3
from config import DATABASE_PATH, MAX_ROWS

ALLOWED_TABLES = {
    "customers",
    "products",
    "orders",
    "order_items"
}


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def list_tables():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    return {
        "success": True,
        "tables": [row["name"] for row in rows]
    }


def search_database(table, limit=10):
    if table not in ALLOWED_TABLES:
        return {
            "success": False,
            "error": "Table is not allowed."
        }

    try:
        limit = min(int(limit), MAX_ROWS)

        connection = get_connection()

        rows = connection.execute(
            f"SELECT * FROM {table} LIMIT ?",
            (limit,)
        ).fetchall()

        connection.close()

        return {
            "success": True,
            "table": table,
            "rows": [dict(row) for row in rows]
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }
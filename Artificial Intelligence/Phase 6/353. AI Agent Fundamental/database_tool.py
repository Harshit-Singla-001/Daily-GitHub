import sqlite3

from config import DATABASE_PATH, MAX_ROWS

ALLOWED_TABLES = {
    "customers",
    "products",
    "orders",
    "order_items"
}

def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection

def list_tables():
    try:
        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)

        tables = [
            row["name"]
            for row in cursor.fetchall()
        ]

        connection.close()

        return {
            "success": True,
            "tables": tables
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }

def search_database(table, limit=20):
    try:
        table = table.strip().lower()

        if table not in ALLOWED_TABLES:
            return {
                "success": False,
                "error": (
                    f"Table '{table}' is not allowed."
                )
            }

        limit = min(
            max(int(limit), 1),
            MAX_ROWS
        )

        connection = get_connection()

        cursor = connection.cursor()

        query = f"""
            SELECT *
            FROM {table}
            LIMIT ?
        """

        cursor.execute(
            query,
            (limit,)
        )

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        connection.close()

        return {
            "success": True,
            "table": table,
            "columns": columns,
            "rows": [
                dict(row)
                for row in rows
            ]
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }
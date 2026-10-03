import sqlite3

from config import DATABASE_PATH


ALLOWED_TABLES = {
    "customers",
    "products",
    "orders",
    "order_items"
}


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection


def list_tables():
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        return [
            row["name"]
            for row in rows
        ]

    finally:
        connection.close()


def search_database(
    table_name,
    limit=20
):
    table_name = str(
        table_name
    ).strip().lower()

    if table_name not in ALLOWED_TABLES:
        raise ValueError(
            f"Table '{table_name}' is not allowed."
        )

    try:
        limit = int(limit)
    except (
        ValueError,
        TypeError
    ):
        limit = 20

    limit = max(
        1,
        min(limit, 100)
    )

    connection = get_connection()

    try:
        query = (
            f'SELECT * FROM "{table_name}" '
            f"LIMIT ?"
        )

        rows = connection.execute(
            query,
            (limit,)
        ).fetchall()

        return {
            "table": table_name,
            "count": len(rows),
            "rows": [
                dict(row)
                for row in rows
            ]
        }

    finally:
        connection.close()
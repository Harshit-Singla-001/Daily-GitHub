import sqlite3
import os

from config import DATABASE_PATH, DATABASE_FOLDER

def get_connection():
    os.makedirs(DATABASE_FOLDER, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            city TEXT,
            state TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id)
                REFERENCES orders(order_id),
            FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        );
    """)

    connection.commit()

    seed_database(connection)

    connection.close()

def seed_database(connection):
    cursor = connection.cursor()

    customer_count = cursor.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    if customer_count > 0:
        return

    customers = [
        ("Harshit Singla", "harshit@example.com", "Mandi Gobindgarh", "Punjab"),
        ("Aman Sharma", "aman@example.com", "Chandigarh", "Chandigarh"),
        ("Rahul Verma", "rahul@example.com", "Mohali", "Punjab"),
        ("Priya Kapoor", "priya@example.com", "Delhi", "Delhi"),
        ("Neha Gupta", "neha@example.com", "Ludhiana", "Punjab"),
        ("Arjun Mehta", "arjun@example.com", "Jaipur", "Rajasthan"),
        ("Simran Kaur", "simran@example.com", "Amritsar", "Punjab"),
        ("Rohan Malhotra", "rohan@example.com", "Mumbai", "Maharashtra")
    ]

    cursor.executemany(
        """
        INSERT INTO customers
        (name, email, city, state)
        VALUES (?, ?, ?, ?)
        """,
        customers
    )

    products = [
        ("Laptop", "Electronics", 65000, 15),
        ("Wireless Mouse", "Electronics", 1200, 50),
        ("Keyboard", "Electronics", 2500, 30),
        ("Monitor", "Electronics", 18000, 20),
        ("Headphones", "Accessories", 3500, 40),
        ("Backpack", "Accessories", 2200, 25),
        ("Notebook", "Stationery", 150, 100),
        ("Pen Set", "Stationery", 300, 80),
        ("Desk Lamp", "Home", 1800, 35),
        ("Office Chair", "Furniture", 12000, 10)
    ]

    cursor.executemany(
        """
        INSERT INTO products
        (name, category, price, stock)
        VALUES (?, ?, ?, ?)
        """,
        products
    )

    orders = [
        (1, "2026-09-01"),
        (2, "2026-09-02"),
        (3, "2026-09-03"),
        (1, "2026-09-04"),
        (5, "2026-09-05"),
        (4, "2026-09-06"),
        (7, "2026-09-07"),
        (8, "2026-09-08")
    ]

    cursor.executemany(
        """
        INSERT INTO orders
        (customer_id, order_date)
        VALUES (?, ?)
        """,
        orders
    )

    order_items = [
        (1, 1, 1),
        (1, 2, 2),
        (2, 3, 1),
        (2, 5, 1),
        (3, 6, 2),
        (3, 7, 5),
        (4, 4, 1),
        (5, 10, 1),
        (5, 2, 1),
        (6, 8, 3),
        (7, 1, 1),
        (8, 9, 2)
    ]

    cursor.executemany(
        """
        INSERT INTO order_items
        (order_id, product_id, quantity)
        VALUES (?, ?, ?)
        """,
        order_items
    )

    connection.commit()

def get_schema():
    connection = get_connection()
    cursor = connection.cursor()

    tables = cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
    """).fetchall()

    schema = []

    for table in tables:
        table_name = table["name"]

        columns = cursor.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()

        column_data = []

        for column in columns:
            column_data.append({
                "name": column["name"],
                "type": column["type"],
                "primary_key": bool(column["pk"])
            })

        schema.append({
            "table": table_name,
            "columns": column_data
        })

    connection.close()

    return schema

def schema_as_text():
    schema = get_schema()
    lines = []

    for table in schema:
        lines.append(f"TABLE {table['table']}")

        for column in table["columns"]:
            lines.append(
                f"  - {column['name']} ({column['type']})"
            )

        lines.append("")

    return "\n".join(lines)

def execute_query(sql):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchmany(100)

        columns = [
            description[0]
            for description in cursor.description
        ]

        return {
            "columns": columns,
            "rows": [
                dict(row)
                for row in rows
            ]
        }

    finally:
        connection.close()
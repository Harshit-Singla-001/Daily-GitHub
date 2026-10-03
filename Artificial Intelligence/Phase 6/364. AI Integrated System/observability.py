import os
import sqlite3

from config import DATABASE_FOLDER, DATABASE_PATH


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    os.makedirs(
        DATABASE_FOLDER,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE SCHEMA
# ============================================================

def initialize_observability():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,

                input_text TEXT,
                response_text TEXT,

                status TEXT NOT NULL,

                latency_ms REAL DEFAULT 0,

                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                thinking_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,

                capability TEXT,

                memory_used INTEGER DEFAULT 0,
                rag_used INTEGER DEFAULT 0,
                tools_used INTEGER DEFAULT 0,

                error_type TEXT,
                error_message TEXT
            )
            """
        )

        # ----------------------------------------------------
        # Migration support
        # ----------------------------------------------------
        #
        # If the database was created using an older version
        # of this project, CREATE TABLE IF NOT EXISTS will NOT
        # add the new columns.
        #
        # Therefore we check the existing columns and add any
        # missing ones.
        # ----------------------------------------------------

        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(ai_requests)"
            ).fetchall()
        }

        required_columns = {
            "thinking_tokens": "INTEGER DEFAULT 0",
            "capability": "TEXT",
            "memory_used": "INTEGER DEFAULT 0",
            "rag_used": "INTEGER DEFAULT 0",
            "tools_used": "INTEGER DEFAULT 0",
            "error_type": "TEXT",
            "error_message": "TEXT"
        }

        for column_name, column_definition in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(
                    f"""
                    ALTER TABLE ai_requests
                    ADD COLUMN {column_name}
                    {column_definition}
                    """
                )

        # ----------------------------------------------------
        # Indexes
        # ----------------------------------------------------

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ai_requests_status
            ON ai_requests(status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ai_requests_timestamp
            ON ai_requests(timestamp)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ai_requests_model
            ON ai_requests(model)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_ai_requests_capability
            ON ai_requests(capability)
            """
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def initialize_database():
    initialize_observability()


# ============================================================
# SAVE REQUEST
# ============================================================

def save_request(
    request_id,
    timestamp,
    model,
    input_text,
    response_text,
    status,
    latency_ms,
    input_tokens=0,
    output_tokens=0,
    thinking_tokens=0,
    total_tokens=0,
    capability=None,
    memory_used=False,
    rag_used=False,
    tools_used=False,
    error_type=None,
    error_message=None
):
    connection = get_connection()

    try:
        # Make sure migrations are applied before inserting.
        _ensure_columns(connection)

        connection.execute(
            """
            INSERT INTO ai_requests (
                request_id,
                timestamp,
                model,
                input_text,
                response_text,
                status,
                latency_ms,

                input_tokens,
                output_tokens,
                thinking_tokens,
                total_tokens,

                capability,

                memory_used,
                rag_used,
                tools_used,

                error_type,
                error_message
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?,
                ?, ?, ?,
                ?, ?
            )
            """,
            (
                request_id,
                timestamp,
                model,
                input_text,
                response_text,
                status,
                latency_ms,

                input_tokens,
                output_tokens,
                thinking_tokens,
                total_tokens,

                capability,

                int(bool(memory_used)),
                int(bool(rag_used)),
                int(bool(tools_used)),

                error_type,
                error_message
            )
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# ENSURE DATABASE COLUMNS
# ============================================================

def _ensure_columns(connection):
    existing_columns = {
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(ai_requests)"
        ).fetchall()
    }

    required_columns = {
        "thinking_tokens": "INTEGER DEFAULT 0",
        "capability": "TEXT",
        "memory_used": "INTEGER DEFAULT 0",
        "rag_used": "INTEGER DEFAULT 0",
        "tools_used": "INTEGER DEFAULT 0",
        "error_type": "TEXT",
        "error_message": "TEXT"
    }

    for column_name, column_definition in required_columns.items():
        if column_name not in existing_columns:
            connection.execute(
                f"""
                ALTER TABLE ai_requests
                ADD COLUMN {column_name}
                {column_definition}
                """
            )


# ============================================================
# GET METRICS
# ============================================================

def get_metrics():
    connection = get_connection()

    try:
        total_requests = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            """
        ).fetchone()["count"]

        successful_requests = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE status = 'SUCCESS'
            """
        ).fetchone()["count"]

        failed_requests = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE status = 'ERROR'
            """
        ).fetchone()["count"]

        average_latency = connection.execute(
            """
            SELECT AVG(latency_ms) AS average
            FROM ai_requests
            WHERE status = 'SUCCESS'
            """
        ).fetchone()["average"]

        minimum_latency = connection.execute(
            """
            SELECT MIN(latency_ms) AS minimum
            FROM ai_requests
            WHERE status = 'SUCCESS'
            """
        ).fetchone()["minimum"]

        maximum_latency = connection.execute(
            """
            SELECT MAX(latency_ms) AS maximum
            FROM ai_requests
            WHERE status = 'SUCCESS'
            """
        ).fetchone()["maximum"]

        total_tokens = connection.execute(
            """
            SELECT COALESCE(
                SUM(total_tokens),
                0
            ) AS total
            FROM ai_requests
            """
        ).fetchone()["total"]

        average_tokens = connection.execute(
            """
            SELECT AVG(total_tokens) AS average
            FROM ai_requests
            WHERE status = 'SUCCESS'
            """
        ).fetchone()["average"]

        memory_requests = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE memory_used = 1
            """
        ).fetchone()["count"]

        rag_requests = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE rag_used = 1
            """
        ).fetchone()["count"]

        tool_requests = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE tools_used = 1
            """
        ).fetchone()["count"]

        if total_requests:
            success_rate = (
                successful_requests /
                total_requests
            ) * 100

            error_rate = (
                failed_requests /
                total_requests
            ) * 100
        else:
            success_rate = 0
            error_rate = 0

        return {
            "total_requests": int(total_requests),
            "successful_requests": int(successful_requests),
            "failed_requests": int(failed_requests),

            "success_rate": round(
                success_rate,
                2
            ),

            "error_rate": round(
                error_rate,
                2
            ),

            "average_latency_ms": round(
                float(average_latency or 0),
                2
            ),

            "minimum_latency_ms": round(
                float(minimum_latency or 0),
                2
            ),

            "maximum_latency_ms": round(
                float(maximum_latency or 0),
                2
            ),

            "total_tokens": int(
                total_tokens or 0
            ),

            "average_tokens": round(
                float(average_tokens or 0),
                2
            ),

            "memory_requests": int(
                memory_requests
            ),

            "rag_requests": int(
                rag_requests
            ),

            "tool_requests": int(
                tool_requests
            )
        }

    finally:
        connection.close()


# ============================================================
# GET REQUEST BY ID
# ============================================================

def get_request_by_id(request_id):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM ai_requests
            WHERE request_id = ?
            """,
            (request_id,)
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


# ============================================================
# GET RECENT REQUESTS
# ============================================================

def get_recent_requests(limit=20):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                request_id,
                timestamp,
                model,
                input_text,
                response_text,
                status,
                latency_ms,

                input_tokens,
                output_tokens,
                thinking_tokens,
                total_tokens,

                capability,

                memory_used,
                rag_used,
                tools_used,

                error_type,
                error_message

            FROM ai_requests

            ORDER BY id DESC

            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()


# ============================================================
# REQUEST COUNT
# ============================================================

def get_request_count():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            """
        ).fetchone()

        return int(
            result["count"]
        )

    finally:
        connection.close()
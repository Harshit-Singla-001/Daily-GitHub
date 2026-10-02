import os
import sqlite3

from config import DATABASE_PATH, DATABASE_FOLDER

def get_connection():
    os.makedirs(DATABASE_FOLDER, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection

def initialize_database():
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
                total_tokens INTEGER DEFAULT 0,
                error_type TEXT,
                error_message TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ai_requests_status
            ON ai_requests(status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ai_requests_timestamp
            ON ai_requests(timestamp)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ai_requests_model
            ON ai_requests(model)
            """
        )

        connection.commit()

    finally:
        connection.close()

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
    total_tokens=0,
    error_type=None,
    error_message=None
):
    connection = get_connection()

    try:
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
                total_tokens,
                error_type,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                total_tokens,
                error_type,
                error_message
            )
        )

        connection.commit()

    finally:
        connection.close()

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

def get_recent_requests(limit=20):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                request_id,
                timestamp,
                model,
                status,
                latency_ms,
                input_tokens,
                output_tokens,
                total_tokens,
                error_type
            FROM ai_requests
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()
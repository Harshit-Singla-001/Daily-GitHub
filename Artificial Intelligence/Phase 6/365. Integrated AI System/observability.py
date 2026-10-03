import os
import sqlite3
from datetime import datetime, timezone

from config import (
    DATABASE_FOLDER,
    DATABASE_PATH
)


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
                total_tokens INTEGER DEFAULT 0,
                rag_used INTEGER DEFAULT 0,
                memory_used INTEGER DEFAULT 0,
                tools_used TEXT,
                error_type TEXT,
                error_message TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_requests_timestamp
            ON ai_requests(timestamp)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_requests_status
            ON ai_requests(status)
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_request(
    request_id,
    model,
    input_text,
    response_text,
    status,
    latency_ms,
    input_tokens=0,
    output_tokens=0,
    total_tokens=0,
    rag_used=False,
    memory_used=False,
    tools_used="",
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
                rag_used,
                memory_used,
                tools_used,
                error_type,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                datetime.now(
                    timezone.utc
                ).isoformat(),
                model,
                input_text,
                response_text,
                status,
                latency_ms,
                input_tokens,
                output_tokens,
                total_tokens,
                int(rag_used),
                int(memory_used),
                tools_used,
                error_type,
                error_message
            )
        )

        connection.commit()

    finally:
        connection.close()


def get_metrics():
    connection = get_connection()

    try:
        total = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            """
        ).fetchone()["count"]

        successful = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE status = 'SUCCESS'
            """
        ).fetchone()["count"]

        failed = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM ai_requests
            WHERE status = 'ERROR'
            """
        ).fetchone()["count"]

        average_latency = connection.execute(
            """
            SELECT AVG(latency_ms) AS value
            FROM ai_requests
            """
        ).fetchone()["value"]

        total_tokens = connection.execute(
            """
            SELECT COALESCE(
                SUM(total_tokens),
                0
            ) AS value
            FROM ai_requests
            """
        ).fetchone()["value"]

        success_rate = (
            (successful / total) * 100
            if total
            else 0
        )

        return {
            "total_requests": int(
                total
            ),
            "successful_requests": int(
                successful
            ),
            "failed_requests": int(
                failed
            ),
            "success_rate": round(
                success_rate,
                2
            ),
            "average_latency_ms": round(
                float(
                    average_latency or 0
                ),
                2
            ),
            "total_tokens": int(
                total_tokens or 0
            )
        }

    finally:
        connection.close()


def get_recent_requests(
    limit=20
):
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
                rag_used,
                memory_used,
                tools_used,
                error_type
            FROM ai_requests
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                limit,
            )
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()


def get_request_by_id(
    request_id
):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM ai_requests
            WHERE request_id = ?
            """,
            (
                request_id,
            )
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()
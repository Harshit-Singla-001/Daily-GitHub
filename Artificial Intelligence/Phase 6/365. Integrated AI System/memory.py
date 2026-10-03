import os
import sqlite3
from datetime import datetime, timezone

from config import DATABASE_FOLDER, DATABASE_PATH, MAX_MEMORY_MESSAGES


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


def initialize_memory():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_conversations_session
            ON conversations(session_id)
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_message(
    session_id,
    role,
    message
):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO conversations (
                session_id,
                role,
                message,
                timestamp
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                message,
                datetime.now(
                    timezone.utc
                ).isoformat()
            )
        )

        connection.commit()

    finally:
        connection.close()


def get_memory(
    session_id,
    limit=None
):
    if limit is None:
        limit = MAX_MEMORY_MESSAGES

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT role, message, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                session_id,
                limit
            )
        ).fetchall()

        rows = list(reversed(rows))

        return [
            {
                "role": row["role"],
                "message": row["message"],
                "timestamp": row["timestamp"]
            }
            for row in rows
        ]

    finally:
        connection.close()


def clear_memory(session_id):
    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM conversations
            WHERE session_id = ?
            """,
            (session_id,)
        )

        connection.commit()

    finally:
        connection.close()


def count_memory(session_id):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM conversations
            WHERE session_id = ?
            """,
            (session_id,)
        ).fetchone()

        return int(row["count"])

    finally:
        connection.close()
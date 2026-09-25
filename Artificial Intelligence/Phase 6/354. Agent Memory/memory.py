import sqlite3
import json
from datetime import datetime
from config import MEMORY_DATABASE_PATH, SHORT_TERM_MESSAGES

SHORT_TERM_MEMORY = {}


def get_connection():
    connection = sqlite3.connect(MEMORY_DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_memory_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            memory_value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, memory_key)
        )
    """)

    connection.commit()
    connection.close()


def add_short_term_message(user_id, role, content):
    if user_id not in SHORT_TERM_MEMORY:
        SHORT_TERM_MEMORY[user_id] = []

    SHORT_TERM_MEMORY[user_id].append({
        "role": role,
        "content": content
    })

    if len(SHORT_TERM_MEMORY[user_id]) > SHORT_TERM_MESSAGES:
        SHORT_TERM_MEMORY[user_id] = SHORT_TERM_MEMORY[user_id][-SHORT_TERM_MESSAGES:]


def get_short_term_memory(user_id):
    return SHORT_TERM_MEMORY.get(user_id, [])


def clear_short_term_memory(user_id):
    SHORT_TERM_MEMORY.pop(user_id, None)


def save_conversation(user_id, role, content):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO conversations
        (user_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            role,
            content,
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


def get_conversation_history(user_id, limit=20):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT role, content, created_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit)
    ).fetchall()

    connection.close()

    rows = list(reversed(rows))

    return [
        {
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]


def save_user_memory(user_id, memory_key, memory_value):
    connection = get_connection()
    now = datetime.now().isoformat()

    connection.execute(
        """
        INSERT INTO user_memory
        (user_id, memory_key, memory_value, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, memory_key)
        DO UPDATE SET
            memory_value = excluded.memory_value,
            updated_at = excluded.updated_at
        """,
        (
            user_id,
            memory_key,
            memory_value,
            now,
            now
        )
    )

    connection.commit()
    connection.close()


def get_user_memories(user_id):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT memory_key, memory_value, updated_at
        FROM user_memory
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return [
        {
            "key": row["memory_key"],
            "value": row["memory_value"],
            "updated_at": row["updated_at"]
        }
        for row in rows
    ]


def delete_user_memory(user_id, memory_key):
    connection = get_connection()

    connection.execute(
        """
        DELETE FROM user_memory
        WHERE user_id = ? AND memory_key = ?
        """,
        (user_id, memory_key)
    )

    connection.commit()
    connection.close()


def clear_user_history(user_id):
    connection = get_connection()

    connection.execute(
        "DELETE FROM conversations WHERE user_id = ?",
        (user_id,)
    )

    connection.execute(
        "DELETE FROM user_memory WHERE user_id = ?",
        (user_id,)
    )

    connection.commit()
    connection.close()

    clear_short_term_memory(user_id)


def build_memory_context(user_id):
    short_term = get_short_term_memory(user_id)
    persistent = get_user_memories(user_id)

    context = []

    if persistent:
        context.append("PERSISTENT USER MEMORY:")

        for item in persistent:
            context.append(
                f"- {item['key']}: {item['value']}"
            )

    if short_term:
        context.append("\nRECENT CONVERSATION:")

        for message in short_term:
            context.append(
                f"{message['role'].upper()}: {message['content']}"
            )

    return "\n".join(context)
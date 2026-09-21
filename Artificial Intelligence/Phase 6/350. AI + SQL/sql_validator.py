import re

FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "UPSERT",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "REINDEX",
    "ANALYZE"
}

def normalize_sql(sql):
    sql = sql.strip()

    sql = re.sub(
        r"```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```",
        "",
        sql
    )

    return sql.strip()

def has_multiple_statements(sql):
    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    return len(statements) > 1

def contains_forbidden_keyword(sql):
    upper_sql = sql.upper()

    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, upper_sql):
            return keyword

    return None

def validate_sql(sql):
    sql = normalize_sql(sql)

    if not sql:
        return False, "Generated SQL is empty."

    if has_multiple_statements(sql):
        return False, "Multiple SQL statements are not allowed."

    forbidden = contains_forbidden_keyword(sql)

    if forbidden:
        return False, (
            f"SQL operation '{forbidden}' is not allowed."
        )

    if not re.match(
        r"^\s*(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE
    ):
        return False, (
            "Only SELECT queries are allowed."
        )

    if "--" in sql or "/*" in sql or "*/" in sql:
        return False, (
            "SQL comments are not allowed."
        )

    return True, "SQL is safe."
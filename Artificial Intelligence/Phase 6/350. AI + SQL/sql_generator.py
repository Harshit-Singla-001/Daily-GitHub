import re
from google import genai

from config import API_KEY, MODEL
from database import schema_as_text

client = genai.Client(api_key=API_KEY)

def generate_sql(question):
    schema = schema_as_text()

    prompt = f"""
You are a SQL generation assistant.

Convert the user's natural-language request into SQLite SQL.

DATABASE SCHEMA:

{schema}

USER REQUEST:
{question}

STRICT RULES:

1. Generate ONLY one SQL statement.
2. The SQL must be read-only.
3. Only SELECT statements are allowed.
4. Do not generate INSERT.
5. Do not generate UPDATE.
6. Do not generate DELETE.
7. Do not generate DROP.
8. Do not generate ALTER.
9. Do not generate CREATE.
10. Do not generate TRUNCATE.
11. Do not generate PRAGMA.
12. Do not generate ATTACH or DETACH.
13. Use only tables and columns present in the schema.
14. Do not invent columns.
15. Do not use markdown.
16. Do not explain the SQL.
17. Return only the SQL query.

SQL:
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    sql = response.text.strip()

    sql = re.sub(
        r"^```sql\s*|\s*```$",
        "",
        sql,
        flags=re.IGNORECASE
    ).strip()

    return sql
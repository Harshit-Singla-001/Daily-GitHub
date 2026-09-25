from google import genai

from config import API_KEY, MODEL

client = genai.Client(api_key=API_KEY)

def generate_response(
    user_input,
    category,
    processed_result
):
    if category == "CALCULATION":
        result = processed_result["result"]

        return f"The answer is {result}."

    if category == "DATABASE":
        return generate_database_response(
            user_input,
            processed_result
        )

    if category == "QUESTION":
        return processed_result["result"]

    if category == "GENERAL":
        return processed_result["result"]

    return "Unable to generate a response."

def generate_database_response(
    user_input,
    processed_result
):
    response = client.models.generate_content(
        model=MODEL,
        contents=f"""
Answer the user's database question using ONLY
the database information provided below.

User question:
{user_input}

Database table:
{processed_result.get("table")}

Columns:
{processed_result.get("columns")}

Rows:
{processed_result.get("rows")}

Do not invent information.
Give a concise and useful answer.
"""
    )

    return response.text
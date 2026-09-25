import json
from google import genai

from config import API_KEY, MODEL

client = genai.Client(api_key=API_KEY)

CLASSIFICATION_PROMPT = """
Classify the user's request into exactly one of these categories:

QUESTION
CALCULATION
DATABASE
GENERAL

Definitions:

QUESTION:
Questions asking for an explanation, definition, concept, or knowledge.

CALCULATION:
Requests involving mathematical calculations.

DATABASE:
Requests asking about customers, products, orders, or database records.

GENERAL:
Anything that does not fit the other categories.

Return ONLY valid JSON:

{
    "category": "QUESTION",
    "reason": "short reason"
}
"""

def classify_request(user_input):
    response = client.models.generate_content(
        model=MODEL,
        contents=f"""
{CLASSIFICATION_PROMPT}

User request:
{user_input}
"""
    )

    text = response.text.strip()

    try:
        result = json.loads(text)

        category = result.get("category", "GENERAL").upper()

        allowed_categories = {
            "QUESTION",
            "CALCULATION",
            "DATABASE",
            "GENERAL"
        }

        if category not in allowed_categories:
            category = "GENERAL"

        return {
            "success": True,
            "category": category,
            "reason": result.get("reason", "")
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "category": "GENERAL",
            "reason": "Classification response was not valid JSON."
        }
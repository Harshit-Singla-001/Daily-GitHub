from google import genai
from google.genai import types

from config import API_KEY, MODEL


client = genai.Client(
    api_key=API_KEY
)


SYSTEM_PROMPT = """
You are an AI document analysis assistant.

You receive text extracted from an image or document.

Your job is to analyze ONLY the information provided in
the extracted text.

Important rules:
- Do not invent missing information.
- If OCR text appears incomplete or unclear, mention it.
- Preserve important numbers, names, dates and facts.
- If the user asks for a summary, provide a structured summary.
- If the user asks for key points, use a bullet list.
- If the user asks a question, answer from the provided text.
- If the answer is not present in the text, clearly say so.
- Make the output easy to read.
"""


def analyze_text(
    extracted_text,
    user_prompt
):
    if not extracted_text.strip():
        return {
            "success": False,
            "error": "No text was extracted."
        }

    prompt = f"""
DOCUMENT TEXT:

{extracted_text}

USER REQUEST:

{user_prompt}

Analyze the document text and answer the user's request.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )

        return {
            "success": True,
            "analysis": (
                response.text
                or "No analysis generated."
            )
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def generate_summary(
    extracted_text
):
    return analyze_text(
        extracted_text,
        """
Create a concise but useful summary.

Use:
## Summary

## Key Points

## Important Information

Keep important names, dates, numbers and facts.
"""
    )


def extract_key_information(
    extracted_text
):
    return analyze_text(
        extracted_text,
        """
Extract the most important information from this document.

Organize the response into:
## Names
## Dates
## Numbers
## Important Facts
## Other Important Information

If a category is not available, say "Not found".
"""
    )
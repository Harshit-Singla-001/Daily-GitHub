from google import genai

from config import API_KEY, LLM_MODEL


client = genai.Client(
    api_key=API_KEY
)


SYSTEM_PROMPT = """
You are a helpful voice assistant.

Answer the user's question clearly and naturally.

Keep responses concise because your response
will be converted into speech.

Do not use markdown tables.

Avoid unnecessary formatting.

If the user asks a simple question,
give a direct answer.

If the user asks for an explanation,
give a short but useful explanation.
"""


def generate_response(transcript):
    if not transcript:
        return {
            "success": False,
            "error": "Transcript is empty."
        }

    try:
        prompt = f"""
{SYSTEM_PROMPT}

User said:

{transcript}

Generate the response that should be spoken back to the user.
"""

        interaction = client.interactions.create(
            model=LLM_MODEL,
            input=prompt
        )

        response_text = (
            interaction.output_text
            or ""
        ).strip()

        if not response_text:
            return {
                "success": False,
                "error": "The LLM returned an empty response."
            }

        return {
            "success": True,
            "text": response_text
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }
import os

from google import genai
from google.genai import types

from config import API_KEY, MODEL


client = genai.Client(
    api_key=API_KEY
)


SYSTEM_PROMPT = """
You are a helpful multimodal AI assistant.

Analyze the provided image carefully.

When analyzing an image:
- Describe only what can reasonably be observed.
- Do not invent details.
- Clearly mention uncertainty when something is unclear.
- Identify important objects, text, colors, layout and visual relationships when relevant.
- If the user asks a specific question, focus on answering that question.
- If text is visible in the image, transcribe important text when requested.
- Do not claim to know information that cannot be determined from the image.
"""


def analyze_image(image_path, user_prompt):
    try:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=get_mime_type(image_path)
        )

        prompt = f"""
Analyze this image.

User request:
{user_prompt}

Provide a clear and useful answer.
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=prompt
                        ),
                        image_part
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )

        return {
            "success": True,
            "analysis": response.text or "No analysis generated."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def get_mime_type(image_path):
    extension = os.path.splitext(
        image_path
    )[1].lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }

    return mime_types.get(
        extension,
        "application/octet-stream"
    )
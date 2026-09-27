import base64
import os
import uuid

from google import genai

from config import (
    API_KEY,
    MODEL,
    GENERATED_FOLDER
)


client = genai.Client(
    api_key=API_KEY
)


def generate_image(prompt):
    if not prompt or not prompt.strip():
        return {
            "success": False,
            "error": "Prompt cannot be empty."
        }

    prompt = prompt.strip()

    try:
        interaction = client.interactions.create(
            model=MODEL,
            input=prompt
        )

        output_image = getattr(
            interaction,
            "output_image",
            None
        )

        if output_image is None:
            return {
                "success": False,
                "error": (
                    "The AI did not return an image."
                )
            }

        image_data = output_image.data

        if not image_data:
            return {
                "success": False,
                "error": (
                    "The generated image "
                    "contains no data."
                )
            }

        image_bytes = base64.b64decode(
            image_data
        )

        filename = (
            f"{uuid.uuid4().hex}.png"
        )

        file_path = os.path.join(
            GENERATED_FOLDER,
            filename
        )

        with open(
            file_path,
            "wb"
        ) as file:
            file.write(
                image_bytes
            )

        return {
            "success": True,
            "filename": filename,
            "path": file_path
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }
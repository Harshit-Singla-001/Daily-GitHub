import base64
import os
import uuid

from google import genai

from config import (
    API_KEY,
    TTS_MODEL,
    AUDIO_FOLDER
)


client = genai.Client(
    api_key=API_KEY
)


def generate_speech(text):
    if not text:
        return {
            "success": False,
            "error": "Text is empty."
        }

    try:
        interaction = client.interactions.create(
            model=TTS_MODEL,
            input=[
                {
                    "type": "user_input",
                    "content": [
                        {
                            "type": "text",
                            "text": text,
                            "annotations": [
                                {
                                    "type": "speech_metadata",
                                    "style": "friendly, natural and clear"
                                }
                            ]
                        }
                    ]
                }
            ],
            response_format={
                "type": "audio"
            },
            generation_config={
                "speech_config": [
                    {
                        "voice": "Kore"
                    }
                ]
            }
        )

        output_audio = getattr(
            interaction,
            "output_audio",
            None
        )

        if output_audio is None:
            return {
                "success": False,
                "error": "TTS did not return audio."
            }

        audio_data = output_audio.data

        if not audio_data:
            return {
                "success": False,
                "error": "Generated audio contains no data."
            }

        audio_bytes = base64.b64decode(
            audio_data
        )

        filename = (
            f"{uuid.uuid4().hex}.wav"
        )

        file_path = os.path.join(
            AUDIO_FOLDER,
            filename
        )

        with open(
            file_path,
            "wb"
        ) as file:
            file.write(audio_bytes)

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
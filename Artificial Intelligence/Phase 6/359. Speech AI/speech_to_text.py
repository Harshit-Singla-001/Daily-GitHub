
import time
from google import genai
from config import API_KEY, STT_MODEL

client = genai.Client(api_key=API_KEY)

MAX_WAIT_TIME = 60
POLL_INTERVAL = 2

def transcribe_audio(file_path):
    try:
        print("Uploading audio...")
        audio_file = client.files.upload(file=file_path)

        print(f"Uploaded file: {audio_file.name}")
        print(f"Initial state: {audio_file.state}")

        start_time = time.time()

        while True:
            if audio_file.state:
                state = audio_file.state.name
            else:
                state = "UNKNOWN"

            print(f"File state: {state}")

            if state == "ACTIVE":
                break

            if state == "FAILED":
                error_message = getattr(audio_file, "error", None)
                return {
                    "success": False,
                    "error": f"Gemini failed to process the audio file: {error_message}"
                }

            if time.time() - start_time > MAX_WAIT_TIME:
                return {
                    "success": False,
                    "error": "Audio file processing timed out. Please try again."
                }

            time.sleep(POLL_INTERVAL)

            audio_file = client.files.get(name=audio_file.name)

        print("Audio file is ACTIVE. Starting transcription...")

        interaction = client.interactions.create(
            model=STT_MODEL,
            input=[
                {
                    "type": "audio",
                    "uri": audio_file.uri,
                    "mime_type": audio_file.mime_type
                }
            ]
        )

        transcript = (interaction.output_text or "").strip()

        if not transcript:
            return {
                "success": False,
                "error": "No speech was detected in the audio."
            }

        return {
            "success": True,
            "text": transcript
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }

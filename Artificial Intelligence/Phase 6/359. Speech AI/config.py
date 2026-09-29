import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

STT_MODEL = (
    os.getenv("GEMINI_STT_MODEL")
    or "gemini-3.5-transcribe"
)

LLM_MODEL = (
    os.getenv("GEMINI_LLM_MODEL")
    or "gemini-3.8-flash"
)

TTS_MODEL = (
    os.getenv("GEMINI_TTS_MODEL")
    or "gemini-3.8-flash-tts"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

AUDIO_FOLDER = os.path.join(
    BASE_DIR,
    "generated_audio"
)

MAX_AUDIO_SIZE = 15 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY or GOOGLE_API_KEY is missing from .env"
    )
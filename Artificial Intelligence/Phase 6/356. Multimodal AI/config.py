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

MODEL = (
    os.getenv("GEMINI_MODEL")
    or os.getenv("MODEL_NAME")
    or os.getenv("MODEL")
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY or GOOGLE_API_KEY is missing in .env"
    )

if not MODEL:
    raise ValueError(
        "GEMINI_MODEL or MODEL_NAME or MODEL is missing in .env"
    )

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)
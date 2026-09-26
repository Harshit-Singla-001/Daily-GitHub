import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

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

TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "pdf",
    "docx",
    "txt"
}

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}

ALLOWED_DOCUMENT_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
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
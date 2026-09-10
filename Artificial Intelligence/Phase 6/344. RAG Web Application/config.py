import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")


if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found in .env"
    )

if not GEMINI_MODEL:
    raise RuntimeError(
        "GEMINI_MODEL not found in .env"
    )


UPLOAD_FOLDER = BASE_DIR / "documents"
DATA_FOLDER = BASE_DIR / "data"

UPLOAD_FOLDER.mkdir(exist_ok=True)
DATA_FOLDER.mkdir(exist_ok=True)


ALLOWED_EXTENSIONS = {
    "txt",
    "pdf",
    "docx",
    "csv"
}

MAX_FILE_SIZE = 10 * 1024 * 1024

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

TOP_K = 4

EMBEDDING_MODEL = "gemini-embedding-001"
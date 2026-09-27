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
    os.getenv("GEMINI_IMAGE_MODEL")
    or os.getenv("IMAGE_MODEL")
    or "gemini-3.1-flash-image"
)

GENERATED_FOLDER = os.path.join(
    BASE_DIR,
    "generated_images"
)

MAX_PROMPT_LENGTH = 4000

os.makedirs(
    GENERATED_FOLDER,
    exist_ok=True
)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY or GOOGLE_API_KEY "
        "is missing in .env"
    )
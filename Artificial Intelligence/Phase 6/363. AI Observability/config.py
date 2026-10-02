import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL = (
    os.getenv("GEMINI_MODEL")
    or os.getenv("MODEL_NAME")
    or os.getenv("MODEL")
)

MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "2000"))
MAX_OUTPUT_LENGTH = int(os.getenv("MAX_OUTPUT_LENGTH", "5000"))

DATABASE_FOLDER = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(
    DATABASE_FOLDER,
    "observability.db"
)

LOG_FOLDER = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(
    LOG_FOLDER,
    "ai_app.log"
)

os.makedirs(DATABASE_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY or GOOGLE_API_KEY is missing in .env"
    )

if not MODEL:
    raise ValueError(
        "GEMINI_MODEL, MODEL_NAME or MODEL is missing in .env"
    )
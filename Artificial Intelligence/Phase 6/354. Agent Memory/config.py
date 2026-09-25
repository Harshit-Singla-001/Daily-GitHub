import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL = os.getenv("GEMINI_MODEL") or os.getenv("MODEL_NAME") or os.getenv("MODEL")

DATABASE_FOLDER = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_FOLDER, "assistant.db")

MEMORY_FOLDER = os.path.join(BASE_DIR, "memory")
MEMORY_DATABASE_PATH = os.path.join(MEMORY_FOLDER, "agent_memory.db")

FILES_FOLDER = os.path.join(BASE_DIR, "files")

MAX_ROWS = 100
MAX_AGENT_STEPS = 6
SHORT_TERM_MESSAGES = 10

if not API_KEY:
    raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY is missing in .env")

if not MODEL:
    raise ValueError("GEMINI_MODEL or MODEL_NAME or MODEL is missing in .env")

os.makedirs(DATABASE_FOLDER, exist_ok=True)
os.makedirs(MEMORY_FOLDER, exist_ok=True)
os.makedirs(FILES_FOLDER, exist_ok=True)
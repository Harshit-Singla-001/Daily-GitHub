import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL = os.getenv("GEMINI_MODEL") or os.getenv("MODEL_NAME") or os.getenv("MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or "gemini-embedding-001"

UPLOAD_FOLDER = "uploads"
VECTOR_STORE_PATH = "other_files/vector_store"
EVALUATION_FILE = "evaluation/test_questions.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
TOP_K = 5
SIMILARITY_THRESHOLD = 0.35

if not API_KEY:
    raise ValueError("Gemini API key is missing from .env")

if not MODEL:
    raise ValueError("Gemini model is missing from .env")
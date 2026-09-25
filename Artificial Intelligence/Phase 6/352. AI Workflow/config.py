import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL = os.getenv("GEMINI_MODEL") or os.getenv("MODEL_NAME") or os.getenv("MODEL")

if not API_KEY:
    raise ValueError("Gemini API key is missing from .env")

if not MODEL:
    raise ValueError("Gemini model is missing from .env")
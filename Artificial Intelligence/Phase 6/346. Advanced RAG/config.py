import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-001"
)

CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", "1000")
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", "150")
)

TOP_K = int(
    os.getenv("TOP_K", "5")
)

SIMILARITY_THRESHOLD = float(
    os.getenv(
        "SIMILARITY_THRESHOLD",
        "0.60"
    )
)

MAX_CONTEXT_CHUNKS = int(
    os.getenv(
        "MAX_CONTEXT_CHUNKS",
        "5"
    )
)

UPLOAD_FOLDER = "uploads"
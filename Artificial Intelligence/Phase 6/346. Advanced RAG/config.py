import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

GEMINI_MODEL = (
    os.getenv("GEMINI_MODEL")
    or os.getenv("MODEL_NAME")
    or os.getenv("MODEL")
)

EMBEDDING_MODEL = (
    os.getenv("EMBEDDING_MODEL")
    or "gemini-embedding-001"
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
    os.getenv("SIMILARITY_THRESHOLD", "0.60")
)

MAX_CONTEXT_CHUNKS = int(
    os.getenv("MAX_CONTEXT_CHUNKS", "5")
)

MAX_FILE_SIZE_MB = int(
    os.getenv("MAX_FILE_SIZE_MB", "20")
)

UPLOAD_FOLDER = "uploads"

VECTOR_STORE_FOLDER = os.path.join(
    "other_files",
    "vector_store"
)

FAISS_INDEX_PATH = os.path.join(
    VECTOR_STORE_FOLDER,
    "index.faiss"
)

METADATA_PATH = os.path.join(
    VECTOR_STORE_FOLDER,
    "metadata.json"
)

ALLOWED_EXTENSIONS = {
    "txt",
    "pdf",
    "docx",
    "csv"
}

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from the .env file."
    )

if not GEMINI_MODEL:
    raise ValueError(
        "GEMINI_MODEL is missing from the .env file."
    )

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_STORE_FOLDER, exist_ok=True)
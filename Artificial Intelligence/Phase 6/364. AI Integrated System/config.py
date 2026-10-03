import os
from dotenv import load_dotenv

# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

# ============================================================
# GEMINI CONFIGURATION
# ============================================================

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

MODEL = (
    os.getenv("GEMINI_MODEL")
    or os.getenv("MODEL_NAME")
    or os.getenv("MODEL")
)

# ============================================================
# APPLICATION LIMITS
# ============================================================

MAX_INPUT_LENGTH = int(
    os.getenv("MAX_INPUT_LENGTH", "2000")
)

MAX_OUTPUT_LENGTH = int(
    os.getenv("MAX_OUTPUT_LENGTH", "5000")
)

MAX_MEMORY_MESSAGES = int(
    os.getenv("MAX_MEMORY_MESSAGES", "10")
)

MAX_AGENT_STEPS = int(
    os.getenv("MAX_AGENT_STEPS", "6")
)

MAX_SEARCH_RESULTS = int(
    os.getenv("MAX_SEARCH_RESULTS", "10")
)

MAX_CONTEXT_LENGTH = int(
    os.getenv("MAX_CONTEXT_LENGTH", "12000")
)

# ============================================================
# RAG CONFIGURATION
# ============================================================

TOP_K = int(
    os.getenv("TOP_K", "5")
)

SIMILARITY_THRESHOLD = float(
    os.getenv("SIMILARITY_THRESHOLD", "0.35")
)

CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", "800")
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", "120")
)

EMBEDDING_MODEL = (
    os.getenv("EMBEDDING_MODEL")
    or "gemini-embedding-001"
)

EMBEDDING_DIMENSION = int(
    os.getenv("EMBEDDING_DIMENSION", "3072")
)

# ============================================================
# DATABASE
# ============================================================

DATABASE_FOLDER = os.path.join(
    BASE_DIR,
    "database"
)

DATABASE_PATH = os.path.join(
    DATABASE_FOLDER,
    "integrated_ai.db"
)

# ============================================================
# KNOWLEDGE FILES
# ============================================================

KNOWLEDGE_FOLDER = os.path.join(
    BASE_DIR,
    "knowledge"
)

# ============================================================
# VECTOR STORE
# ============================================================

# Main vector store folder
VECTOR_FOLDER = os.path.join(
    BASE_DIR,
    "other_files",
    "vector_store"
)

# Compatibility alias for modules that use the newer name
VECTOR_STORE_FOLDER = VECTOR_FOLDER

VECTOR_STORE_PATH = os.path.join(
    VECTOR_FOLDER,
    "knowledge_vectors.json"
)

# ============================================================
# UPLOADS
# ============================================================

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

MAX_UPLOAD_SIZE_MB = int(
    os.getenv("MAX_UPLOAD_SIZE_MB", "20")
)

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
    ".csv"
}

# ============================================================
# LOGGING
# ============================================================

LOG_FOLDER = os.path.join(
    BASE_DIR,
    "logs"
)

LOG_FILE = os.path.join(
    LOG_FOLDER,
    "ai_app.log"
)

# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

os.makedirs(
    DATABASE_FOLDER,
    exist_ok=True
)

os.makedirs(
    KNOWLEDGE_FOLDER,
    exist_ok=True
)

os.makedirs(
    VECTOR_FOLDER,
    exist_ok=True
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    LOG_FOLDER,
    exist_ok=True
)

# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY or GOOGLE_API_KEY is missing in .env"
    )

if not MODEL:
    raise ValueError(
        "GEMINI_MODEL, MODEL_NAME or MODEL is missing in .env"
    )
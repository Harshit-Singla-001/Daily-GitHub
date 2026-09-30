import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

MODEL_ID = os.getenv(
    "HF_MODEL_ID",
    "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)

MODEL_TASK = os.getenv("HF_MODEL_TASK", "text-classification")
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1000"))

MODELS_FOLDER = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_FOLDER, exist_ok=True)
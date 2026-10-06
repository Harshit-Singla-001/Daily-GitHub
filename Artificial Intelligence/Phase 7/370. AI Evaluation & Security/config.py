import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

AUDIT_LOG_FILE = LOG_DIR / "security_audit.json"

MAX_INPUT_LENGTH = int(
    os.getenv("MAX_INPUT_LENGTH", "5000")
)

MAX_OUTPUT_LENGTH = int(
    os.getenv("MAX_OUTPUT_LENGTH", "10000")
)

RISK_THRESHOLDS = {
    "LOW": 24,
    "MEDIUM": 49,
    "HIGH": 74,
    "CRITICAL": 100,
}
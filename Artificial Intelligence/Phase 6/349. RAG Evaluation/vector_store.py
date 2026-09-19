import os
import json
import numpy as np
from config import VECTOR_STORE_PATH

STORE_FILE = os.path.join(VECTOR_STORE_PATH, "store.json")

def ensure_store():
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

def save_store(records):
    ensure_store()

    with open(STORE_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False)

def load_store():
    if not os.path.exists(STORE_FILE):
        return []

    with open(STORE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def add_records(records):
    existing = load_store()
    existing.extend(records)
    save_store(existing)

def clear_store():
    ensure_store()

    if os.path.exists(STORE_FILE):
        os.remove(STORE_FILE)

def cosine_similarity(vector_a, vector_b):
    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)
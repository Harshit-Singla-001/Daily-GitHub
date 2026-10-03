import json
import math
import os

from config import VECTOR_FOLDER
from embeddings import create_document_embedding


VECTOR_FILE = os.path.join(
    VECTOR_FOLDER,
    "vectors.json"
)


def load_vectors():
    if not os.path.exists(
        VECTOR_FILE
    ):
        return []

    try:
        with open(
            VECTOR_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):
        return []


def save_vectors(vectors):
    os.makedirs(
        VECTOR_FOLDER,
        exist_ok=True
    )

    with open(
        VECTOR_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            vectors,
            file,
            ensure_ascii=False,
            indent=2
        )


def add_chunks(chunks):
    vectors = load_vectors()

    existing_ids = {
        item["chunk_id"]
        for item in vectors
    }

    added = 0

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]

        if chunk_id in existing_ids:
            continue

        embedding = create_document_embedding(
            chunk["text"]
        )

        vectors.append(
            {
                "chunk_id": chunk_id,
                "text": chunk["text"],
                "document": chunk["document"],
                "page": chunk.get("page", 1),
                "section": chunk.get("section", ""),
                "position": chunk.get("position", 0),
                "embedding": embedding
            }
        )

        added += 1

    save_vectors(
        vectors
    )

    return added


def delete_document(
    document_name
):
    vectors = load_vectors()

    filtered = [
        item
        for item in vectors
        if item["document"] != document_name
    ]

    save_vectors(
        filtered
    )

    return len(vectors) - len(filtered)


def get_documents():
    vectors = load_vectors()

    documents = sorted(
        {
            item["document"]
            for item in vectors
        }
    )

    return documents


def cosine_similarity(
    vector_a,
    vector_b
):
    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b
        )
    )

    magnitude_a = math.sqrt(
        sum(
            value * value
            for value in vector_a
        )
    )

    magnitude_b = math.sqrt(
        sum(
            value * value
            for value in vector_b
        )
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )
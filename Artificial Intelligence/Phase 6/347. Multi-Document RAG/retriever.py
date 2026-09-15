import numpy as np

from config import (
    TOP_K,
    SIMILARITY_THRESHOLD,
    MAX_CONTEXT_CHUNKS
)


def cosine_similarity(a, b):
    a = np.array(
        a,
        dtype=np.float32
    )

    b = np.array(
        b,
        dtype=np.float32
    )

    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b)
        / denominator
    )


def retrieve_chunks(
    query_embedding,
    chunks,
    embeddings
):
    results = []

    for chunk, embedding in zip(
        chunks,
        embeddings
    ):
        score = cosine_similarity(
            query_embedding,
            embedding
        )

        results.append({
            "chunk": chunk,
            "score": score
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    candidates = results[:TOP_K]

    filtered = [
        result
        for result in candidates
        if result["score"]
        >= SIMILARITY_THRESHOLD
    ]

    return filtered[
        :MAX_CONTEXT_CHUNKS
    ]